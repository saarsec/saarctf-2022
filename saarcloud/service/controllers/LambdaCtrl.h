#pragma once

#include <drogon/HttpSimpleController.h>
#include <drogon/drogon.h>

namespace drogon {
class StaticFileRouter;
}

using namespace drogon;


class [[maybe_unused]] LambdaCtrl : public drogon::HttpController<LambdaCtrl> {
	std::unique_ptr<drogon::StaticFileRouter> CDNDataRouter;

public:
	LambdaCtrl();

	void handleLambdaRequest(const std::shared_ptr<HttpRequest> &req, std::function<void(const HttpResponsePtr &)> &&callback,
							 const std::string &user, const std::string &path);

	void handleCDNRequest(const std::shared_ptr<HttpRequest> &req, std::function<void(const HttpResponsePtr &)> &&callback);

	METHOD_LIST_BEGIN
		ADD_METHOD_VIA_REGEX(LambdaCtrl::handleLambdaRequest, "/([^/]+)/(.*)");
	METHOD_LIST_END
};
