#include "dbwaller/core/sharded_engine.hpp"
#include "dbwaller/security/claims.hpp"

#include <map>
#include <string>
#include <vector>

int main() {
    const auto fingerprint = dbwaller::security::claims_fingerprint_hex(
        std::vector<std::string>{"reader"},
        std::vector<std::string>{"posts:read"},
        std::map<std::string, std::string>{{"tenant", "example"}},
        16
    );

    if (fingerprint.empty()) {
        return 1;
    }

    dbwaller::core::ShardedEngine::Config config;
    config.num_shards = 2;
    config.enable_compute_pool = false;

    dbwaller::core::ShardedEngine engine(config);

    dbwaller::core::PutOptions options;
    options.ttl_ms = 500;
    options.tags = {"post:42"};

    engine.put("post:42", "cached-value", options);
    const auto cached = engine.get("post:42");
    engine.shutdown();

    return cached && *cached == "cached-value" ? 0 : 1;
}
