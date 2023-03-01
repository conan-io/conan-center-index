#include <foxglove/websocket/websocket_notls.hpp>
#include <foxglove/websocket/websocket_server.hpp>

template<>
void foxglove::Server<foxglove::WebSocketNoTls>::setupTlsHandler() {}

int main() {
    const auto logHandler = [](foxglove::WebSocketLogLevel, char const* msg) {
      std::cout << msg << std::endl;
    };
    foxglove::ServerOptions serverOptions;
    foxglove::Server<foxglove::WebSocketNoTls> server("example", logHandler, serverOptions);
    server.start("127.0.0.1", 0);
    server.stop();
    return 0;
}
