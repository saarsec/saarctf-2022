#include <drogon/drogon.h>
#include "jsengine/DatabaseEngine.h"

void HostRouting(const drogon::HttpRequestPtr &request) {
	auto &path = (std::string &) request->path();
	// Get the innermost subdomain (from Host header)
	std::string host = request->getHeader("Host");
	auto pos = host.find('.');
	if (pos != std::string::npos) host = host.substr(0, pos);
	pos = host.find(':');
	if (pos != std::string::npos) host = host.substr(0, pos);
	// default host
	if (host.empty() || host == "www" || host == "localhost" || host == "10" || host == "127")
		host = "default";
	// add to path
	path = "/" + host + path;
}

int main() {
	DbEngine.Init();
	std::string rootPath = "../";
	//Set HTTP listener address and port
	drogon::app().addListener("0.0.0.0", 8080);
	//Load config file
	drogon::app().loadConfigFile("../config.json");
	drogon::app().registerPreRoutingAdvice(HostRouting);
	drogon::app().setDocumentRoot(rootPath + "static");
	//Run HTTP framework,the method will block in the internal event loop
	drogon::app().run();
	return 0;
}
