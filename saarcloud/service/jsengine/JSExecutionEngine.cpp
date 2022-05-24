#include "JSExecutionEngine.h"
#include "LambdaRequest.h"

using namespace v8;

bool JSSiteEngine::handleLambdaRequest(LambdaRequest *req) {
	v8::Isolate::Scope isolate_scope(isolate);
	v8::HandleScope handle_scope(isolate);
	auto context = contextHandle.Get(isolate);
	v8::Context::Scope context_scope(context);

	TryCatch try_catch(isolate);

	Local<Object> requestObject = threadEngine->lambdaRequestTemplate.Get(isolate)->NewInstance(context).ToLocalChecked();
	req->MoveToV8Heap(requestObject);

	Local<Value> argv[1] = {requestObject};
	v8::Local<v8::Function> handleLambdaRequestJSFunction = v8::Local<v8::Function>::New(isolate, handleLambdaRequestJS);
	Local<Value> result;
	if (!handleLambdaRequestJSFunction->Call(context, context->Global(), 1, argv).ToLocal(&result)) {
		String::Utf8Value error(isolate, try_catch.Exception());
		throw std::runtime_error(*error ? *error : "(unknown)");
	}
	auto res = result->IsBoolean() && result.As<Boolean>()->Value();
	isolate->LowMemoryNotification();
	return res;
}

#define CONTEXT_ADD_FUNCTION(name, function) if (!context->Global()->Set(context, v8::String::NewFromUtf8Literal(isolate, name), function).ToChecked()) abort()
#define CONTEXT_ADD_FUNCTION_OBJ(name, function) if (!context->Global()->Set(context, v8::String::NewFromUtf8Literal(isolate, name), function).ToChecked()) abort()

void JSSiteEngine::defineInterface(bool isDefault) {
	auto context = contextHandle.Get(isolate);
	v8::Context::Scope context_scope(context);
	if (isDefault) {
		CONTEXT_ADD_FUNCTION("writeSaarLambda", threadEngine->writeSaarLambdaFunction.Get(isolate));
		CONTEXT_ADD_FUNCTION("writeSaarCDN", threadEngine->writeSaarCDNFunction.Get(isolate));
		CONTEXT_ADD_FUNCTION("generateRandomToken", threadEngine->generateRandomTokenFunction.Get(isolate));
		CONTEXT_ADD_FUNCTION("passwordHash", threadEngine->passwordHashFunction.Get(isolate));
	}
	CONTEXT_ADD_FUNCTION("sha256", threadEngine->sha256Function.Get(isolate));
	CONTEXT_ADD_FUNCTION("println", threadEngine->printlnFunction.Get(isolate));
	CONTEXT_ADD_FUNCTION_OBJ("HTTPResponse", threadEngine->lambdaResponseTemplate.Get(isolate)->GetFunction(context).ToLocalChecked());
	CONTEXT_ADD_FUNCTION_OBJ("SaarRDSInterface", threadEngine->saarRDSTemplate.Get(isolate)->NewInstance(context).ToLocalChecked());
	runScript(readLibraryFile(), "library.js");

	Local<Value> value;
	if (!context->Global()->Get(context, String::NewFromUtf8Literal(isolate, "handleLambdaRequest")).ToLocal(&value) || !value->IsFunction()) {
		throw std::runtime_error("Function \"handleLambdaRequest\" not defined");
	}
	handleLambdaRequestJS.Reset(isolate, value.As<Function>());
}


void JSThreadEngine::checkSiteEngineTimeout() {
	std::lock_guard lock(currentSiteEngineMutex);
	if (currentSiteEngine) {
		auto dt = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - currentSiteEngineStart);
		if (dt.count() > 2000) {
			std::cerr << "Terminating execution because timeout. Current site: " << currentSiteEngine->name << std::endl;
			JSThreadEngineGen.reportResourceViolation(currentSiteEngine->name);
			terminate();
		}
	}
}

void JSThreadEngine::terminate() {
	isolate->TerminateExecution();
	// Use a fresh engine for future requests
	if (this->loop->isInLoopThread()) {
		siteEngineForSite.clear();
		JSThreadEngineGen.terminate(this);
	} else {
		this->loop->runInLoop([this]() { this->terminate(); });
	}
}


thread_local std::optional<std::shared_ptr<JSThreadEngine>> JSThreadEngineGenerator::currentEngine;
JSThreadEngineGenerator JSThreadEngineGen;
