#include <jsengine/LambdaRequest.h>
#include <jsengine/JSExecutionEngine.h>
#include <plugins/AccessLogsPlugin.h>
#include "AccessLogsCtrl.h"

void AccessLogsCtrl::handleNewConnection(const HttpRequestPtr &req, const WebSocketConnectionPtr &wsConnPtr) {
	auto callback = [wsConnPtr](const HttpResponsePtr &response){
		wsConnPtr->send(response->body().data(), response->body().length());
		wsConnPtr->shutdown();
		wsConnPtr->forceClose();
	};
	auto request = new LambdaRequest(req, std::move(callback));
	auto requestLock = request->Lock(); // request must stay in memory until this method finishes, even if moved to V8's heap
	auto threadEngine = JSThreadEngineGen.getEngine();
	auto siteEngine = threadEngine->getSiteEngine(threadEngine, "default");
	if (siteEngine && !siteEngine->handleLambdaRequest(request) && !request->hasResponded) {
		// Logging controller, take over!
		if (req->method() == drogon::Get && req->path() == "/default/logs") {
			// accept this connection - enter in log message list
			app().getPlugin<AccessLogsPlugin>()->addLogChannel(request->request->getParameter("user"), wsConnPtr);
			request->hasResponded = true;
			threadEngine->returnSiteEngine();
			return;
		}
	}
	// Terminate connection
	wsConnPtr->send("Not authenticated!");
	wsConnPtr->shutdown();
	wsConnPtr->forceClose();
	request->hasResponded = true;
	threadEngine->returnSiteEngine();
}

void AccessLogsCtrl::handleNewMessage(const WebSocketConnectionPtr &wsConnPtr, std::string &&message, const WebSocketMessageType &type) {}

void AccessLogsCtrl::handleConnectionClosed(const WebSocketConnectionPtr &wsConnPtr) {
	app().getPlugin<AccessLogsPlugin>()->removeLogChannel(wsConnPtr);
}
