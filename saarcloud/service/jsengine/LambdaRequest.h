#ifndef SAARCLOUD_JSEXECUTIONENGINE_H
#define SAARCLOUD_JSEXECUTIONENGINE_H

#include <memory>
#include <functional>
#include <utility>
#include <drogon/drogon.h>
#include "v8.h"

using namespace drogon;
using namespace v8;

/**
 * Object is owned and managed by V8's heap.
 * Any outside reference must be guarded by "Lock()"
 * @tparam T
 * @tparam C a unique constant to identify type T
 */
template<class T, int C>
class V8HeapManageableObject {
public:
	v8::Persistent<v8::Object> handle;
	bool usedOutsideHeap = false;

	void MoveToV8Heap(v8::Local<v8::Object> object) {
		if (object->InternalFieldCount() < 2)
			abort();
		object->SetInternalField(0, Number::New(object->GetIsolate(), C));
		object->SetInternalField(1, External::New(object->GetIsolate(), static_cast<T *>(this)));
		handle.Reset(object->GetIsolate(), object);
		// Delete this instance when object gets GC'ed
		handle.SetWeak(static_cast<T *>(this), [](const v8::WeakCallbackInfo<T> &data) {
			auto this_ = data.GetParameter();
			this_->handle.Reset();
			if (!this_->usedOutsideHeap) delete this_;
		}, WeakCallbackType::kParameter);
	}

	static T *Unwrap(v8::Local<v8::Value> value) {
		if (!value->IsObject()) return nullptr;
		auto object = value.As<Object>();
		if (object->InternalFieldCount() < 2) return nullptr;
		if (!object->GetInternalField(0)->IsNumber() || object->GetInternalField(0).As<Number>()->Value() != C) return nullptr;
		if (!object->GetInternalField(1)->IsExternal()) return nullptr;
		return static_cast<T *>(object->GetInternalField(1).As<External>()->Value());
	}

	static T *UnwrapOrException(v8::Isolate *isolate, v8::Local<v8::Value> value) {
		auto t = Unwrap(value);
		if (!t)
			isolate->ThrowException(v8::Exception::TypeError(String::NewFromUtf8Literal(isolate, "Wrong type")));
		return t;
	}

	struct Locker {
		V8HeapManageableObject<T, C> *_ptr = nullptr;

		Locker(Locker &) = delete;

		~Locker() {
			if (_ptr) {
				_ptr->Unlock();
			}
		}
	};

	/**
	 * Keep the returned Locker object as long as you keep this object outside of V8's heap
	 * @return
	 */
	Locker Lock() {
		usedOutsideHeap = true;
		return {this};
	}

	void Unlock() {
		usedOutsideHeap = false;
		if (handle.IsEmpty()) delete static_cast<T *>(this);
	}
};


class LambdaRequest : public V8HeapManageableObject<LambdaRequest, 1> {
public:
	std::shared_ptr<HttpRequest> request;
	std::function<void(const HttpResponsePtr &)> callback;
	bool hasResponded = false;

	LambdaRequest(std::shared_ptr<HttpRequest> request, const std::function<void(const HttpResponsePtr &)> &&callback)
			: request(std::move(request)), callback(callback) {}

	~LambdaRequest() {
		done();
	}

	void respond(const HttpResponsePtr &response) {
		if (hasResponded) {
			return;
		}
		hasResponded = true;
		callback(response);
	}

	void done() {
		if (!hasResponded) {
			auto resp = HttpResponse::newHttpResponse();
			resp->setStatusCode(drogon::k501NotImplemented);
			resp->setContentTypeCode(drogon::CT_TEXT_PLAIN);
			resp->setBody("Programming error, your request remained unhandled.");
			respond(resp);
		}
	}
};


class LambdaResponse : public V8HeapManageableObject<LambdaResponse, 2> {
public:
	drogon::HttpResponsePtr rsp = HttpResponse::newHttpResponse();

	LambdaResponse() = default;

	~LambdaResponse() = default;
};

#endif //SAARCLOUD_JSEXECUTIONENGINE_H
