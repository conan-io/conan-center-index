#include <foxglove/websocket/websocket_notls.hpp>
#include <foxglove/websocket/websocket_server.hpp>

template<>
void foxglove::Server<foxglove::WebSocketNoTls>::setupTlsHandler() {}

int main() {
    // Note: Server instance is only initiated here and not started. This is similar to how it's
    // done in the websocketpp recipe.
    const auto logHandler = [](foxglove::WebSocketLogLevel, char const* msg) {
      std::cout << msg << std::endl;
    };
    foxglove::ServerOptions serverOptions;
    foxglove::Server<foxglove::WebSocketNoTls> server("example", logHandler, serverOptions);
    (void)server;
    return 0;
}
