#ifndef SAARCLOUD_DATABASEENGINE_H
#define SAARCLOUD_DATABASEENGINE_H

#include <mutex>
#include <map>
#include <drogon/orm/DbClient.h>
#include <trantor/net/EventLoop.h>
#include <filesystem>
#include <regex>
#include "utils.h"


namespace {
std::vector<std::string> splitString(const std::string &input, const std::string &regex) {
	// passing -1 as the submatch index parameter performs splitting
	std::regex re(regex);
	std::sregex_token_iterator first {input.begin(), input.end(), re, -1}, last;
	return {first, last};
}
}


struct DatabaseClient {
	std::shared_ptr<drogon::orm::DbClient> client;
	bool unusedForCleanup = false;
};


class DatabaseEngine {
	std::mutex mutex;
	std::map<std::string, DatabaseClient> clients;
public:

	std::shared_ptr<drogon::orm::DbClient> getClient(const std::string &dbname) {
		std::lock_guard<std::mutex> lock(mutex);
		auto it = clients.find(dbname);
		if (it != clients.end()) {
			it->second.unusedForCleanup = false;
			return it->second.client;
		}
		auto conn = "filename=../databases/" + dbname + ".sqlite3";
		return (clients[dbname] = {drogon::orm::DbClient::newSqlite3Client(conn, 1), false}).client;
	}

	/**
	 * Close databases that have been open for longer than 5 minutes without usage.
	 */
	void checkForUnusedClients() {
		std::lock_guard<std::mutex> lock(mutex);
		for (auto it = clients.begin(); it != clients.end();) {
			if (it->second.unusedForCleanup) {
				it = clients.erase(it);
			} else {
				it->second.unusedForCleanup = true;
				it++;
			}
		}
	}

	template<typename FUNCTION1, typename FUNCTION2, typename... Arguments>
	void execSqlAsync(trantor::EventLoop *loop, const std::string &dbname, const std::string &sql,
					  FUNCTION1 &&rCallback,
					  FUNCTION2 &&exceptCallback,
					  Arguments &&... args) {
		auto client = getClient(dbname);
		client->execSqlAsync(sql, [loop, rCallback = std::forward<FUNCTION1>(rCallback)](const drogon::orm::Result &r) {
			drogon::orm::Result r2 = r;
			loop->runInLoop([r = std::move(r2), rCallback]() {
				rCallback(r);
			});
		}, [loop, exceptCallback = std::forward<FUNCTION2>(exceptCallback)](const drogon::orm::DrogonDbException &e) {
			const auto *s = dynamic_cast<const drogon::orm::SqlError *>(&e);
			if (s) {
				drogon::orm::SqlError e2 = *s;
				loop->runInLoop([e = std::move(e2), exceptCallback]() {
					exceptCallback(e);
				});
			} else {
				drogon::orm::DrogonDbException e2 = e;
				loop->runInLoop([e = std::move(e2), exceptCallback]() {
					exceptCallback(e);
				});
			}
		}, std::forward<Arguments>(args)...);
	}

	void Init() {
		std::filesystem::create_directories("../databases");
		auto sql = readFile("../default.sql");
		auto client = getClient("default");
		for (const auto &sqlPart: splitString(sql, "\n\n")) {
			client->execSqlAsync(sqlPart, [](const drogon::orm::Result &r) {}, [sql = std::string(sqlPart)](const drogon::orm::DrogonDbException &e) {
				std::cerr << "Could not init default database! " << e.base().what() << " in " << sql << std::endl;
			});
		}

		// Cleanup
		drogon::app().getLoop()->runEvery(300.0, [this]() { this->checkForUnusedClients(); });
	}

};

extern DatabaseEngine DbEngine;

#endif //SAARCLOUD_DATABASEENGINE_H
