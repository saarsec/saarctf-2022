#include <memory>
#include <iostream>
#include <utility>
#include <uuid/uuid.h>
#include <sys/stat.h>
#include <openssl/sha.h>
#include "v8.h"
#include "libplatform/libplatform.h"
#include "caching.h"
#include "LambdaRequest.h"
#include "DatabaseEngine.h"
#include "utils.h"

namespace {
ConstRefCacheDecorator<std::string> readLibraryFile([]() { return readFile("../library.js"); });
}

using namespace v8;


class JSSiteEngine;

class JSThreadEngine;

/**
 * The JS engine containing a single site script.
 */
class JSSiteEngine {
	friend JSThreadEngine;

	std::string name;
	std::shared_ptr<JSThreadEngine> threadEngine;
	v8::Isolate *isolate;
	v8::Global<v8::Context> contextHandle;
	v8::Global<v8::Function> handleLambdaRequestJS;
	bool unusedForCleanup = false;

public:
	JSSiteEngine(std::shared_ptr<JSThreadEngine> threadEngine, v8::Isolate *isolate, const std::string &name)
	: threadEngine(std::move(threadEngine)), isolate(isolate), name(name) {
		v8::Isolate::Scope isolate_scope(isolate);
		v8::HandleScope handle_scope(isolate);
		this->contextHandle.Reset(isolate, v8::Context::New(isolate));
	}

	~JSSiteEngine() {
		contextHandle.Reset();
		handleLambdaRequestJS.Reset();
	}

	void Init(const std::string &script, const std::string &siteName) {
		v8::Isolate::Scope isolate_scope(isolate);
		v8::HandleScope handle_scope(isolate);
		defineInterface(siteName == "default");
		runScript(script, siteName + ".js");
	}

	void defineInterface(bool isDefault = false);

	bool runScript(const std::string &script, const std::string &scriptName = "<anonymous>") {
		auto context = contextHandle.Get(isolate);
		v8::Context::Scope context_scope(context);
		v8::TryCatch try_catch(isolate);
		auto ScriptName = String::NewFromUtf8(isolate, scriptName.c_str(), NewStringType::kInternalized).ToLocalChecked();

		// Isolate contexts on a per-site level (if that didn't already happen)
		if (!context->GetSecurityToken()->IsString()) {
			context->SetSecurityToken(ScriptName);
		}

		// Compile script
		v8::Local<v8::Script> compiled_script;
		auto scriptVar = v8::String::NewFromUtf8(isolate, script.c_str()).ToLocalChecked();
		if (!v8::Script::Compile(context, scriptVar, new ScriptOrigin(isolate, ScriptName)).ToLocal(&compiled_script)) {
			v8::String::Utf8Value error(isolate, try_catch.Exception());
			std::cerr << "(in RunScript) Could not compile: " << *error << "\n";
			return false;
		}

		// Execute script
		v8::Local<v8::Value> result;
		if (!compiled_script->Run(context).ToLocal(&result)) {
			v8::String::Utf8Value error(isolate, try_catch.Exception());
			if (error.length())
				std::cerr << "(in RunScript) Execution error: " << *error << "\n";
			return false;
		}

		return true;
	}

public:
	/**
	 *
	 * @param req Request that should be moved (and be managed by) V8's heap
	 * @return true if JS/Lambda handles this request, false otherwise
	 */
	bool handleLambdaRequest(LambdaRequest *req);

	bool runScriptFromExternal(const std::string &script, const std::string &scriptName = "<anonymous>") {
		v8::Isolate::Scope isolate_scope(isolate);
		v8::HandleScope handle_scope(isolate);
		return runScript(script, scriptName);
	}
};

/**
 * Represents 1 independent v8 isolate per thread, that must be used only within that thread.
 */
class JSThreadEngine {
	friend JSSiteEngine;

	v8::Isolate::CreateParams create_params;
	v8::Isolate *isolate;
	v8::Global<v8::Function> printlnFunction;
	v8::Global<v8::Function> writeSaarLambdaFunction;
	v8::Global<v8::Function> writeSaarCDNFunction;
	v8::Global<v8::Function> generateRandomTokenFunction;
	v8::Global<v8::Function> sha256Function;
	v8::Global<v8::Function> passwordHashFunction;
	v8::Global<v8::ObjectTemplate> lambdaRequestTemplate;
	v8::Global<v8::FunctionTemplate> lambdaResponseTemplate;
	v8::Global<v8::ObjectTemplate> saarRDSTemplate;
	std::set<std::string> authorizedDatabases;
	std::map<std::string, std::shared_ptr<JSSiteEngine>> siteEngineForSite;

	std::shared_ptr<JSSiteEngine> currentSiteEngine = nullptr;
	std::chrono::steady_clock::time_point currentSiteEngineStart;
	std::mutex currentSiteEngineMutex;

	trantor::EventLoop *loop = nullptr;
	trantor::TimerId checkForUnusedSitesTimer;

public:
	JSThreadEngine() {
		create_params.array_buffer_allocator = v8::ArrayBuffer::Allocator::NewDefaultAllocator();
		create_params.allow_atomics_wait = false;
		create_params.constraints.ConfigureDefaultsFromHeapSize(0, 128 * 1024 * 1024);
		isolate = v8::Isolate::New(create_params);
		// Terminate engine if we run out of memory
		isolate->AddNearHeapLimitCallback((NearHeapLimitCallback) &onOutOfMemoryCallback, this);
#ifndef TEST_PROGRAM
		initEventLoop();
#endif
		initTemplates();
	}

	~JSThreadEngine() {
		printlnFunction.Reset();
		writeSaarLambdaFunction.Reset();
		writeSaarCDNFunction.Reset();
		generateRandomTokenFunction.Reset();
		sha256Function.Reset();
		passwordHashFunction.Reset();
		lambdaRequestTemplate.Reset();
		lambdaResponseTemplate.Reset();
		saarRDSTemplate.Reset();

		isolate->Dispose();
		delete create_params.array_buffer_allocator;
		if (loop) {
			loop->invalidateTimer(checkForUnusedSitesTimer);
		}
	}

	static size_t onOutOfMemoryCallback(JSThreadEngine *this_, size_t current_heap_limit, size_t initial_heap_limit) {
		std::cerr << "Terminating execution because memory is exhausted. Current site: " << this_->currentSiteEngine->name << std::endl;
		this_->terminate();
		return current_heap_limit * 2;
	}

	void terminate();

	std::shared_ptr<JSSiteEngine> getSiteEngine(const std::shared_ptr<JSThreadEngine> &threadEngine, const std::string &siteName) {
		auto it = siteEngineForSite.find(siteName);
		if (it != siteEngineForSite.end()) {
			setCurrentSiteEngine(it->second);
			return it->second;
		}
		std::string script;
		try {
			script = readFile(SCRIPT_PATH + siteName + ".js");
		} catch (const std::exception &e) {
			std::cerr << "Could not load script for " + siteName + ": " << e.what() << std::endl;
		}
		auto engine = std::make_shared<JSSiteEngine>(threadEngine, isolate, siteName);
		siteEngineForSite[siteName] = engine;
		setCurrentSiteEngine(engine);
		engine->Init(script, siteName);
		return engine;
	}

	void setCurrentSiteEngine(std::shared_ptr<JSSiteEngine> engine) {
		std::lock_guard lock(currentSiteEngineMutex);
		currentSiteEngine = engine;
		currentSiteEngine->unusedForCleanup = false;
		currentSiteEngineStart = std::chrono::steady_clock::now();
	}

	void returnSiteEngine() {
		std::lock_guard lock(currentSiteEngineMutex);
		currentSiteEngine = nullptr;
	}

	/**
	 * Unload sites that use more than 2000ms to process a request.
	 */
	void checkSiteEngineTimeout();

	/**
	 * Unload sites that have no traffic for 5+ minutes
	 */
	void checkForUnusedSites() {
		for (auto it = siteEngineForSite.cbegin(); it != siteEngineForSite.cend();) {
			if (it->second->unusedForCleanup) {
				it = siteEngineForSite.erase(it);
			} else {
				it->second->unusedForCleanup = true;
				it++;
			}
		}
	}

#define LAMBDA_REQUEST_PROPERTY(name, code) lambdaRequest->SetAccessor(String::NewFromUtf8Literal(isolate, name), \
    [](Local<String> property, const PropertyCallbackInfo<Value> &info) {\
        if (auto lambda = LambdaRequest::UnwrapOrException(info.GetIsolate(), info.Holder())) { info.GetReturnValue().Set(code); } \
    })
#define LAMBDA_REQUEST_FUNCTION_START(name) lambdaRequest->Set(isolate, "respond", FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value>& info) { \
    if (auto lambda = LambdaRequest::UnwrapOrException(info.GetIsolate(), info.Holder())) {
#define LAMBDA_REQUEST_FUNCTION_END    }}));

	void initTemplates() {
		v8::Isolate::Scope isolate_scope(isolate);
		v8::HandleScope scope2(isolate);
		auto defaultContext = v8::Context::New(isolate);
		v8::Context::Scope context_scope(defaultContext);

		// ===== Utility functions =====
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto f = v8::Function::New(isolate->GetCurrentContext(), println).ToLocalChecked();
			printlnFunction.Reset(isolate, handle_scope.Escape(f));
		}
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto f = v8::Function::New(isolate->GetCurrentContext(), writeSaarLambda).ToLocalChecked();
			writeSaarLambdaFunction.Reset(isolate, handle_scope.Escape(f));
		}
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto f = v8::Function::New(isolate->GetCurrentContext(), writeSaarCDN).ToLocalChecked();
			writeSaarCDNFunction.Reset(isolate, handle_scope.Escape(f));
		}
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto f = v8::Function::New(isolate->GetCurrentContext(), generateRandomToken).ToLocalChecked();
			generateRandomTokenFunction.Reset(isolate, handle_scope.Escape(f));
		}
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto f = v8::Function::New(isolate->GetCurrentContext(), sha256).ToLocalChecked();
			sha256Function.Reset(isolate, handle_scope.Escape(f));
		}
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto f = v8::Function::New(isolate->GetCurrentContext(), passwordHash).ToLocalChecked();
			passwordHashFunction.Reset(isolate, handle_scope.Escape(f));
		}

		// ===== LambdaRequest JS representation =====
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto lambdaRequest = v8::ObjectTemplate::New(isolate);
			lambdaRequest->SetInternalFieldCount(2);
			LAMBDA_REQUEST_PROPERTY("type", String::NewFromUtf8(info.GetIsolate(), lambda->request->getMethodString()).ToLocalChecked());
			LAMBDA_REQUEST_PROPERTY("path", String::NewFromUtf8(info.GetIsolate(), lambda->request->path().substr(lambda->request->path().find('/', 1)).c_str()).ToLocalChecked());
			LAMBDA_REQUEST_PROPERTY("body", String::NewFromUtf8(info.GetIsolate(), lambda->request->bodyData(), NewStringType::kNormal,
																lambda->request->bodyLength()).ToLocalChecked());
			LAMBDA_REQUEST_PROPERTY("query", String::NewFromUtf8(info.GetIsolate(), lambda->request->query().c_str()).ToLocalChecked());
			LAMBDA_REQUEST_PROPERTY("data", MapToV8(info.GetIsolate(), lambda->request->parameters()));
			LAMBDA_REQUEST_PROPERTY("cookies", MapToV8(info.GetIsolate(), lambda->request->cookies()));
			LAMBDA_REQUEST_FUNCTION_START("respond")
									if (info.Length() >= 1) {
										if (auto response = LambdaResponse::UnwrapOrException(info.GetIsolate(), info[0]))
											lambda->respond(response->rsp);
									}
			LAMBDA_REQUEST_FUNCTION_END
			lambdaRequestTemplate.Reset(isolate, handle_scope.Escape(lambdaRequest));
		}

		// ===== LambdaResponse JS representation =====
		{
			v8::EscapableHandleScope handle_scope(isolate);
			v8::Local<v8::FunctionTemplate> response = v8::FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value> &info) {
				if (info.This()->IsObject() && info.IsConstructCall())
					(new LambdaResponse())->MoveToV8Heap(info.This().As<Object>());
			});
			response->InstanceTemplate()->SetInternalFieldCount(2);
			response->PrototypeTemplate()->Set(isolate, "setBody", FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value> &info) {
				if (auto response = LambdaResponse::UnwrapOrException(info.GetIsolate(), info.Holder())) {
					if (auto body = requireFunctionArgumentAsString(info, 0))
						response->rsp->setBody(*body);
				}
			}));
			response->PrototypeTemplate()->Set(isolate, "setContentType",
											   FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value> &info) {
												   if (auto response = LambdaResponse::UnwrapOrException(info.GetIsolate(), info.Holder())) {
													   if (auto code = requireFunctionArgumentAsInt(info, 0))
														   response->rsp->setContentTypeCode((ContentType) *code);
												   }
											   }));
			response->PrototypeTemplate()->Set(isolate, "setStatusCode",
											   FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value> &info) {
												   if (auto response = LambdaResponse::UnwrapOrException(info.GetIsolate(), info.Holder())) {
													   if (auto code = requireFunctionArgumentAsInt(info, 0))
														   response->rsp->setStatusCode((HttpStatusCode) *code);
												   }
											   }));
			lambdaResponseTemplate.Reset(isolate, handle_scope.Escape(response));
		}

		// ===== saarRDSTemplate JS representation =====
		{
			v8::EscapableHandleScope handle_scope(isolate);
			auto saarRDS = v8::ObjectTemplate::New(isolate);

			saarRDS->Set(isolate, "authorize", FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value> &info) {
				auto this_ = (JSThreadEngine *) info.Data().As<External>()->Value();
				auto db = requireFunctionArgumentAsString(info, 0);
				auto token = requireFunctionArgumentAsString(info, 1);
				if (db && token && isValidName(*db)) {
					std::shared_ptr<JSSiteEngine> currentSite = this_->currentSiteEngine;
					auto resolver = Promise::Resolver::New(currentSite->contextHandle.Get(this_->isolate)).ToLocalChecked();
					info.GetReturnValue().Set(resolver->GetPromise());
					auto resolverHandle = std::make_shared<Global<Promise::Resolver>>(this_->isolate, resolver);
					DbEngine.execSqlAsync(
							this_->loop, "default", "SELECT * FROM rds_databases WHERE dbname = ? AND token = ?",
							[currentSite, resolverHandle, db = *db, this_](const drogon::orm::Result &r) {
								// All that boilerplate code to start execution
								auto isolate = currentSite->isolate;
								v8::Isolate::Scope isolate_scope(isolate);
								v8::HandleScope handle_scope(isolate);
								auto context = currentSite->contextHandle.Get(isolate);
								v8::Context::Scope context_scope(context);
								v8::TryCatch try_catch(isolate);
								currentSite->threadEngine->setCurrentSiteEngine(currentSite);
								// Resolve the promise with db data
								auto ok = r.size() == 1;
								if (ok) {
									this_->authorizedDatabases.insert(db);
								}
								resolverHandle->Get(isolate)->Resolve(currentSite->contextHandle.Get(isolate), Boolean::New(isolate, ok)).Check();
								// Done
								currentSite->threadEngine->returnSiteEngine();

							},
							[currentSite, resolverHandle](const drogon::orm::DrogonDbException &e) {
								// All that boilerplate code to start execution
								auto isolate = currentSite->isolate;
								v8::Isolate::Scope isolate_scope(isolate);
								v8::HandleScope handle_scope(isolate);
								v8::Context::Scope context_scope(currentSite->contextHandle.Get(isolate));
								v8::TryCatch try_catch(isolate);
								currentSite->threadEngine->setCurrentSiteEngine(currentSite);
								// Resolve the promise with db data
								std::cout << "Resolve now ... (false)\n";
								auto error = String::NewFromUtf8(isolate, "DB Error").ToLocalChecked();
								resolverHandle->Get(isolate)->Reject(currentSite->contextHandle.Get(isolate), error).Check();
								// Done
								currentSite->threadEngine->returnSiteEngine();
							}, *db, *token);
				}
			}, External::New(isolate, this)));

			saarRDS->Set(isolate, "execSQL", FunctionTemplate::New(isolate, [](const v8::FunctionCallbackInfo<Value> &info) {
				auto this_ = (JSThreadEngine *) info.Data().As<External>()->Value();
				auto db = requireFunctionArgumentAsString(info, 0);
				auto sql = requireFunctionArgumentAsString(info, 1);
				if (db && sql && isValidName(*db)) {
					std::cerr << "> [" << *db << "] " << *sql << std::endl;
					std::shared_ptr<JSSiteEngine> currentSite = this_->currentSiteEngine;
					auto resolver = Promise::Resolver::New(currentSite->contextHandle.Get(this_->isolate)).ToLocalChecked();
					info.GetReturnValue().Set(resolver->GetPromise());
					if (this_->authorizedDatabases.find(*db) == this_->authorizedDatabases.end()) {
						resolver->Reject(currentSite->contextHandle.Get(this_->isolate),
										 String::NewFromUtf8Literal(this_->isolate, "Authorization necessary!")).Check();
						return;
					}
					auto resolverHandle = std::make_shared<Global<Promise::Resolver>>(this_->isolate, resolver);
					DbEngine.execSqlAsync(
							this_->loop, *db, *sql,
							[currentSite, resolverHandle](const drogon::orm::Result &r) {
								// All that boilerplate code to start execution
								auto isolate = currentSite->isolate;
								v8::Isolate::Scope isolate_scope(isolate);
								v8::HandleScope handle_scope(isolate);
								auto context = currentSite->contextHandle.Get(isolate);
								v8::Context::Scope context_scope(context);
								v8::TryCatch try_catch(isolate);
								currentSite->threadEngine->setCurrentSiteEngine(currentSite);
								// Resolve the promise with db data
								auto results = Array::New(isolate, r.size());
								int rowNumber = 0;
								for (auto &row: r) {
									auto object = Object::New(isolate);
									int colNumber = 0;
									for (auto &field: row) {
										auto key = String::NewFromUtf8(isolate, r.columnName(colNumber++)).ToLocalChecked();
										if (field.isNull()) {
											object->Set(context, key, Null(isolate)).Check();
										} else {
											object->Set(context, key, String::NewFromUtf8(isolate, field.c_str(), NewStringType::kNormal,
																						  field.length()).ToLocalChecked()).Check();
										}
									}
									results->Set(context, rowNumber++, object).Check();
								}
								results->Set(context, String::NewFromUtf8Literal(isolate, "insertId"), Number::New(isolate, r.insertId())).Check();

								resolverHandle->Get(isolate)->Resolve(currentSite->contextHandle.Get(isolate), results).Check();
								// Done
								currentSite->threadEngine->returnSiteEngine();

							},
							[currentSite, resolverHandle](const drogon::orm::DrogonDbException &e) {
								// All that boilerplate code to start execution
								auto isolate = currentSite->isolate;
								v8::Isolate::Scope isolate_scope(isolate);
								v8::HandleScope handle_scope(isolate);
								v8::Context::Scope context_scope(currentSite->contextHandle.Get(isolate));
								v8::TryCatch try_catch(isolate);
								currentSite->threadEngine->setCurrentSiteEngine(currentSite);
								// Resolve the promise with db data
								auto error = String::NewFromUtf8(isolate, e.base().what()).ToLocalChecked();
								resolverHandle->Get(isolate)->Reject(currentSite->contextHandle.Get(isolate), error).Check();
								// Done
								currentSite->threadEngine->returnSiteEngine();
							});
				}
			}, External::New(isolate, this)));

			saarRDSTemplate.Reset(isolate, handle_scope.Escape(saarRDS));
		}
	}

	static std::optional<std::string> requireFunctionArgumentAsString(const v8::FunctionCallbackInfo<Value> &info, int i) {
		if (i < info.Length()) {
			if (info[i]->IsString()) {
				return *String::Utf8Value(info.GetIsolate(), info[i]);
			}
		}
		info.GetIsolate()->ThrowException(String::NewFromUtf8Literal(info.GetIsolate(), "Invalid type, expected string"));
		return {};
	}

	static std::optional<int> requireFunctionArgumentAsInt(const v8::FunctionCallbackInfo<Value> &info, int i) {
		if (i < info.Length()) {
			if (info[i]->IsNumber()) {
				return info[i].As<Number>()->Value();
			}
		}
		info.GetIsolate()->ThrowException(String::NewFromUtf8Literal(info.GetIsolate(), "Invalid type, expected int"));
		return {};
	}

	static void println(const FunctionCallbackInfo<Value> &args) {
		std::cerr << "[Script]";
		for (int i = 0; i < args.Length(); i++) {
			std::cerr << " ";
			Local<Value> arg = args[i];
			if (arg->IsNumber()) {
				std::cerr << arg.As<Number>()->Value();
			} else if (arg->IsString()) {
				std::cerr << *String::Utf8Value(args.GetIsolate(), arg);
			} else if (arg->IsNull()) {
				std::cerr << "null";
			} else if (arg->IsUndefined()) {
				std::cerr << "undefined";
			} else if (arg->IsBoolean()) {
				std::cerr << (arg->IsTrue() ? "true" : "false");
			} else {
				std::cerr << "(type " << *String::Utf8Value(args.GetIsolate(), arg->TypeOf(args.GetIsolate())) << ")";
			}
		}
		std::cerr << "\n";
	}

	static void writeSaarLambda(const FunctionCallbackInfo<Value> &args) {
		auto name = requireFunctionArgumentAsString(args, 0);
		auto code = requireFunctionArgumentAsString(args, 1);
		if (name && code) {
			if (isValidName(*name) && *name != "default") {
				writeFile(SCRIPT_PATH + *name + ".js", *code);
			} else {
				args.GetIsolate()->ThrowException(String::NewFromUtf8Literal(args.GetIsolate(), "Invalid name"));
			}
		} else {
			args.GetIsolate()->ThrowException(String::NewFromUtf8Literal(args.GetIsolate(), "Requires two arguments"));
		}
	}

	static void writeSaarCDN(const FunctionCallbackInfo<Value> &args) {
		auto name = requireFunctionArgumentAsString(args, 0);
		auto filename = requireFunctionArgumentAsString(args, 1);
		auto code = requireFunctionArgumentAsString(args, 2);
		if (name && filename && code) {
			if (isValidName(*name) && *name != "default" && filename->find("..") == std::string::npos) {
				std::string dir = CDN_PATH + *name;
				mkdir(dir.c_str(), 0700);
				writeFile(dir + "/" + *filename, *code);
			} else {
				args.GetIsolate()->ThrowException(String::NewFromUtf8Literal(args.GetIsolate(), "Invalid name"));
			}
		} else {
			args.GetIsolate()->ThrowException(String::NewFromUtf8Literal(args.GetIsolate(), "Requires two arguments"));
		}
	}

	static void generateRandomToken(const FunctionCallbackInfo<Value> &args) {
		uuid_t uu;
		uuid_generate(uu);
		auto token = drogon::utils::binaryStringToHex(uu, 16);
		args.GetReturnValue().Set(String::NewFromUtf8(args.GetIsolate(), token.c_str()).ToLocalChecked());
	}

	static void sha256(const FunctionCallbackInfo<Value> &args) {
		auto input = requireFunctionArgumentAsString(args, 0);
		if (input) {
			unsigned char hash[SHA256_DIGEST_LENGTH];
			SHA256(reinterpret_cast<const unsigned char *>(input->c_str()), input->length(), hash);
			auto hex = drogon::utils::binaryStringToHex(hash, SHA256_DIGEST_LENGTH);
			args.GetReturnValue().Set(String::NewFromUtf8(args.GetIsolate(), hex.c_str()).ToLocalChecked());
		} else {
			args.GetIsolate()->ThrowException(String::NewFromUtf8Literal(args.GetIsolate(), "Requires string argument"));
		}
	}

	static void passwordHash(const FunctionCallbackInfo<Value> &args) {
		auto input = requireFunctionArgumentAsString(args, 0);
		if (input) {
			std::string data = getApplicationSecret() + "|" + *input + "|" + getApplicationSecret();
			unsigned char hash[SHA256_DIGEST_LENGTH];
			SHA256(reinterpret_cast<const unsigned char *>(data.c_str()), data.length(), hash);
			auto hex = drogon::utils::binaryStringToHex(hash, SHA256_DIGEST_LENGTH);
			args.GetReturnValue().Set(String::NewFromUtf8(args.GetIsolate(), hex.c_str()).ToLocalChecked());
		} else {
			args.GetIsolate()->ThrowException(String::NewFromUtf8Literal(args.GetIsolate(), "Requires string argument"));
		}
	}

	/**
	 * Get the current event loop / init the "loop" field of this class
	 */
	void initEventLoop() {
		for (int i = 0; i < drogon::app().getThreadNum(); i++) {
			auto loop = drogon::app().getIOLoop(i);
			if (loop->isInLoopThread()) {
				this->loop = loop;
				checkForUnusedSitesTimer = this->loop->runEvery(300.0, [this]() { this->checkForUnusedSites(); });
				return;
			}
		}
		throw std::runtime_error("Engine must be running in a drogon event loop");
	}
};

/**
 * Manager: Creates and holds a unique thread engine per thread.
 */
class JSThreadEngineGenerator {
	std::unique_ptr<v8::Platform> platform = v8::platform::NewDefaultPlatform();
	static thread_local std::optional<std::shared_ptr<JSThreadEngine>> currentEngine;
	std::map<std::string, int> siteFailureCount;
	std::set<JSThreadEngine *> engines;
	std::mutex cleanupLock;

public:
	inline JSThreadEngineGenerator() {
		v8::V8::InitializePlatform(platform.get());
		v8::V8::InitializeICU("./icudtl.dat");
		v8::V8::Initialize();
		getApplicationSecret(); // generate per-instance secret when application starts first time
		drogon::app().getLoop()->runEvery(1, [this](){ this->checkCleanup(); });
	}

	inline ~JSThreadEngineGenerator() {
		v8::V8::Dispose();
        v8::V8::DisposePlatform();
	}

	inline std::shared_ptr<JSThreadEngine> getEngine() {
		if (!currentEngine) {
			std::lock_guard guard(cleanupLock);
			currentEngine = std::make_shared<JSThreadEngine>();
			engines.insert(currentEngine->get());
		}
		return *currentEngine;
	}

	inline void terminate(JSThreadEngine *engine) {
		if (currentEngine->get() == engine) {
			std::lock_guard guard(cleanupLock);
			currentEngine.reset();
			engines.erase(engine);
		}
	}

	void checkCleanup() {
		std::lock_guard guard(cleanupLock);
		for (auto engine: engines) {
			engine->checkSiteEngineTimeout();
		}
	}

	inline void reportResourceViolation(const std::string &site) {
		// only called from checkCleanup, therefore explicit guard of cleanupLock needed
		if (++siteFailureCount[site] >= 3) {
			std::cerr << "Killing site \"" << site << "\" permanently for multiple recorded resource constraint violations." << std::endl;
			std::string script = SCRIPT_PATH + site + ".js";
			std::string script2 = SCRIPT_PATH + site + ".js.disabled";
			rename(script.c_str(), script2.c_str());
		}
	}
};

extern JSThreadEngineGenerator JSThreadEngineGen;
