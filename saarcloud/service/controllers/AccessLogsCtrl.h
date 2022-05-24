#pragma once

#include <drogon/WebSocketController.h>

using namespace drogon;

class [[maybe_unused]] AccessLogsCtrl : public drogon::WebSocketController<AccessLogsCtrl> {
public:
	void handleNewMessage(const WebSocketConnectionPtr &, std::string &&, const WebSocketMessageType &) override;

	void handleNewConnection(const HttpRequestPtr &, const WebSocketConnectionPtr &) override;

	void handleConnectionClosed(const WebSocketConnectionPtr &) override;

	WS_PATH_LIST_BEGIN
		WS_PATH_ADD("/default/logs");
	WS_PATH_LIST_END
};
