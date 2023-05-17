#include <sw/redis++/redis++.h>

using namespace sw::redis;

int main() {
    try{
        auto redis = Redis("tcp://127.0.0.1:6379");
        redis.set("key", "val");
        redis.rpush("list", {"a", "b", "c"});
    }
    catch(...)
    {
    }

    return 0;
}
