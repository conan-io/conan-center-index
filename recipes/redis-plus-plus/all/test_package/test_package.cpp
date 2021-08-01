#include <sw/redis++/redis++.h>

using namespace sw::redis;

int main() {

    ConnectionOptions opts;
    opts.host = "127.0.0.1";
    opts.port = 6379;

    #ifdef BUILDING_WITH_TLS
    opts.tls.enabled = true;
    #endif

    try{
        auto redis = Redis(opts);
        redis.set("key", "val");
        redis.rpush("list", {"a", "b", "c"});
    }
    catch(...)
    {
    }

    return 0;
}
