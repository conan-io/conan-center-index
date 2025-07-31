#include <websocketpp/server.hpp>
#include <websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/config/asio_client.hpp>
#include <websocketpp/client.hpp>


int main()
{
    websocketpp::server<websocketpp::config::asio> server;

    websocketpp::client<websocketpp::config::asio_tls_client> client;
}
