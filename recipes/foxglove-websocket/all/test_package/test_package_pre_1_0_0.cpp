#include <foxglove/websocket/server.hpp>

int main() {
    // Note: Server instance is only initiated here and not started. This is similar to how it's
    // done in the websocketpp recipe.
    foxglove::websocket::Server server{0, "example"};
    (void)server;
    return 0;
}
