#ifndef SAARCLOUD_UTILS_H
#define SAARCLOUD_UTILS_H

#include <fstream>
#include <v8.h>
#include <uuid/uuid.h>
#include <drogon/drogon.h>

namespace {

	constexpr const char* const SCRIPT_PATH = "../scripts/";
	constexpr const char* const CDN_PATH = "../static/";

	std::string readFile(const std::string &filename) {
		std::ifstream f(filename);
		std::string str;
		if (f.bad() || f.fail())
			throw std::runtime_error("Can't read file");
		f.seekg(0, std::ios::end);
		str.reserve(f.tellg());
		f.seekg(0, std::ios::beg);
		str.assign((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
		return str;
	}

	void writeFile(const std::string &filename, const std::string &content) {
		std::ofstream f(filename, std::ios::out | std::ios::trunc);
		f << content;
		if (f.bad())
			throw std::runtime_error("Can't write file");
	}

	bool isValidName(const std::string &name) {
		if (name.length() < 3 || name.length() > 64) return false;
		for (auto c: name) {
			if ('0' <= c && c <= '9') continue;
			if ('a' <= c && c <= 'z') continue;
			if ('A' <= c && c <= 'Z') continue;
			if (c == '_') continue;
			return false;
		}
		return true;
	}

	v8::Local<v8::Object> MapToV8(v8::Isolate *isolate, const std::unordered_map<std::string, std::string> &map) {
		auto object = v8::Object::New(isolate);
		auto context = isolate->GetCurrentContext();
		for (const auto &it: map) {
			auto key = v8::String::NewFromUtf8(isolate, it.first.c_str()).ToLocalChecked();
			auto value = v8::String::NewFromUtf8(isolate, it.second.c_str()).ToLocalChecked();
			object->Set(context, key, value).Check();
		}
		return object;
	}

	std::string stored_secret;

	std::string getApplicationSecret() {
		if (!stored_secret.empty())
			return stored_secret;
		try {
			stored_secret = readFile("../application_secret");
		} catch (const std::runtime_error &e) {}
		if (stored_secret.empty()) {
			uuid_t uu;
			uuid_generate(uu);
			stored_secret = drogon::utils::binaryStringToHex(uu, 16);
			writeFile("../application_secret", stored_secret);
			std::cerr << "Generated new application secret" << std::endl;
		}
		return stored_secret;
	}
}

#endif //SAARCLOUD_UTILS_H
