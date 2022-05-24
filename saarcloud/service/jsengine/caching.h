#ifndef JSENGINE_CACHING_H
#define JSENGINE_CACHING_H

#include <functional>
#include <map>

template<typename R, typename... A>
class CacheDecorator {
public:
	CacheDecorator(std::function<R(A...)> f) : f_(f) {}

	R operator()(A... a) {
		std::tuple<A...> key(a...);
		auto search = map_.find(key);
		if (search != map_.end()) {
			return search->second;
		}

		auto result = f_(a...);
		map_[key] = result;
		return result;
	}

private:
	std::function<R(A...)> f_;
	std::map<std::tuple<A...>, R> map_;
};


template<typename R>
class ConstRefCacheDecorator {
public:
	explicit ConstRefCacheDecorator(std::function<R()> f) : f_(f) {}

	const R &operator()() {
		if (!result) {
			result = f_();
		}
		return *result;
	}

private:
	std::function<R()> f_ {};
	std::optional<R> result;
};

#endif //JSENGINE_CACHING_H
