#include "node/node.h"

#include <cstdio>

int main() {
    librats::NodeConfig config;
    config.listen_port = 0;  // ephemeral
    librats::Node node(config);
    std::printf("librats peer id: %s\n", node.local_id().short_hex().c_str());
    return 0;
}
