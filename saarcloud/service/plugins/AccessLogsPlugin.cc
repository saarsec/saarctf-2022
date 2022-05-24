#include <drogon/HttpAppFramework.h>
#include "AccessLogsPlugin.h"

using namespace drogon;

void AccessLogsPlugin::initAndStart(const Json::Value &config) {
	app().registerPostHandlingAdvice([this](const HttpRequestPtr &request, const HttpResponsePtr &response) {
		this->logRequest(request, response);
	});
}

void AccessLogsPlugin::shutdown() {}

void AccessLogsPlugin::logRequest(const HttpRequestPtr &request, const HttpResponsePtr &response) {
	auto p = request->path().find('/', 1);
	auto user = request->path().substr(1, p > 0 ? p-1 : request->path().length());

	// get connected websockets
	std::shared_lock ReadLock(mutex);
	auto it = connections.find(user);
	if (it != connections.end()) {
		std::string message =
				request->peerAddr().toIp() + " [" + std::to_string(response->statusCode()) + "] \"" +
				std::string(request->methodString()) + " " + request->path() + "\"";
		for (auto &wsConnPtr: it->second) {
			wsConnPtr->send(message);
		}
	}
}

void AccessLogsPlugin::addLogChannel(const std::string &user, const WebSocketConnectionPtr &wsConnPtr) {
	wsConnPtr->setContext(std::make_shared<std::string>(user));
	std::unique_lock WriteLock(mutex);
	connections[user].insert(wsConnPtr);
}

void AccessLogsPlugin::removeLogChannel(const WebSocketConnectionPtr &wsConnPtr) {
	auto user = wsConnPtr->getContext<std::string>();
	if (!user || user->empty())
		return;
	std::unique_lock WriteLock(mutex);
	auto &listOfConnections = connections[*user];
	listOfConnections.erase(wsConnPtr);
	if (listOfConnections.empty())
		connections.erase(*user);
}
