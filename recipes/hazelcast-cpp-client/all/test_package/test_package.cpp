#include <hazelcast/client/hazelcast_client.h>

int main() {
    hazelcast::client::client_config config;
    config.get_connection_strategy_config().get_retry_config().set_cluster_connect_timeout(std::chrono::seconds(1));

    try {
        auto hz = hazelcast::new_client(std::move(config)).get();
    } catch (std::exception &e) {
    }
    return EXIT_SUCCESS;
}
