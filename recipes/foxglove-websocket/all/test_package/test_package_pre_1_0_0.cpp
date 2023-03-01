#include <foxglove/websocket/server.hpp>

int main() {
    foxglove::websocket::Server server{0, "example"};
    server.getEndpoint().set_timer(0, [&](std::error_code const& ec) {
      server.stop();
    });
    server.run();
    return 0;
}
