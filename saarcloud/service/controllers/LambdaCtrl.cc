#include "LambdaCtrl.h"
#include <memory>
#include <StaticFileRouter.h>
#include <jsengine/JSExecutionEngine.h>
#include <jsengine/LambdaRequest.h>

LambdaCtrl::LambdaCtrl() {
	// Get a list of all event loops
	std::vector<trantor::EventLoop *> loops;
	loops.reserve(drogon::app().getThreadNum() + 1);
	for (int i = 0; i < drogon::app().getThreadNum(); i++) {
		loops.push_back(drogon::app().getIOLoop(i));
	}
	loops.push_back(drogon::app().getLoop());
	// Initialize an additional static file router (to power SaarCDN)
	CDNDataRouter = std::make_unique<StaticFileRouter>();
	CDNDataRouter->init(loops);
	CDNDataRouter->setStaticFilesCacheTime(-1);
}

void LambdaCtrl::handleCDNRequest(const std::shared_ptr<HttpRequest> &req, std::function<void(const HttpResponsePtr &)> &&callback) {
	CDNDataRouter->route((const HttpRequestImplPtr &) req, std::move(callback));
}

void LambdaCtrl::handleLambdaRequest(const std::shared_ptr<HttpRequest> &req, std::function<void(const HttpResponsePtr &)> &&callback,
									 const std::string &user, const std::string &path) {
	if (!isValidName(user)) {
		auto r = HttpResponse::newHttpResponse();
		r->setStatusCode(HttpStatusCode::k500InternalServerError);
		r->setContentTypeCode(drogon::CT_TEXT_PLAIN);
		r->setBody("Invalid username");
		callback(r);
		return;
	}

	auto request = new LambdaRequest(req, std::move(callback));
	auto requestLock = request->Lock(); // request must stay in memory until this method finishes, even if moved to V8's heap
	auto threadEngine = JSThreadEngineGen.getEngine();
	auto siteEngine = threadEngine->getSiteEngine(threadEngine, user);
	try {
		if (siteEngine && !siteEngine->handleLambdaRequest(request) && !request->hasResponded) {
			// This request seems to be for SaarCDN. SaarCDN - take over.
			request->hasResponded = true;
			handleCDNRequest(req, std::move(request->callback));
		}
	} catch (const std::runtime_error &e) {
		std::cerr << "Error: " << e.what() << std::endl;
		auto r = HttpResponse::newHttpResponse();
		r->setStatusCode(HttpStatusCode::k500InternalServerError);
		r->setContentTypeCode(drogon::CT_TEXT_PLAIN);
		r->setBody(e.what());
		request->respond(r);
	}
	threadEngine->returnSiteEngine();
}
