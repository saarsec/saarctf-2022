#pragma once

#include <drogon/plugins/Plugin.h>
#include <drogon/WebSocketConnection.h>
#include <shared_mutex>


class [[maybe_unused]] AccessLogsPlugin : public drogon::Plugin<AccessLogsPlugin> {
	std::shared_mutex mutex;
	std::map<std::string, std::set<drogon::WebSocketConnectionPtr>> connections;

public:
	AccessLogsPlugin() = default;

	/// This method must be called by drogon to initialize and start the plugin.
	/// It must be implemented by the user.
	void initAndStart(const Json::Value &config) override;

	/// This method must be called by drogon to shutdown the plugin.
	/// It must be implemented by the user.
	void shutdown() override;

	void addLogChannel(const std::string &user, const drogon::WebSocketConnectionPtr &wsConnPtr);

	void removeLogChannel(const drogon::WebSocketConnectionPtr &wsConnPtr);

private:
	void logRequest(const drogon::HttpRequestPtr &request, const drogon::HttpResponsePtr &response);
};

