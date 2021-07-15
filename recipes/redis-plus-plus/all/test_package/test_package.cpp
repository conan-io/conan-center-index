#include <sw/redis++/redis++.h>
#include <string>
#if __cplusplus >= 201703L
#include <string_view>
#include <optional>
#endif

using namespace sw::redis;

int main() {
    try{
        auto redis = Redis("tcp://127.0.0.1:6379");
        redis.set("key", "val");
        redis.rpush("list", {"a", "b", "c"});
#if __cplusplus >= 201703L
        std::optional<std::string> val = redis.get("key");
#else
        Optional<std::string> val = redis.get("key");
#endif
    }
    catch(...)
    {
    }

    return 0;
}
