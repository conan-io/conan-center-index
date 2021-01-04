#include <websocketpp/server.hpp>
#include <websocketpp/config/asio_no_tls.hpp>

int main()
{
    websocketpp::server<websocketpp::config::asio> server;
}
