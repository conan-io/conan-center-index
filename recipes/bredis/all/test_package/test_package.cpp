#include <cstdlib>
#include <iostream>

#include "boost/asio.hpp"
#include "bredis/MarkerHelpers.hpp"
#include "bredis/Connection.hpp"

namespace r = bredis;
namespace asio = boost::asio;

int main(int argc, const char** argv) {
  using socket_t = asio::ip::tcp::socket;
  using next_layer_t = socket_t;

  asio::io_context io_service;

  auto ip_address = asio::ip::make_address("127.0.0.1");
  auto port = boost::lexical_cast<std::uint16_t>("6379");

  asio::ip::tcp::endpoint end_point(ip_address, port);

  socket_t socket(io_service, end_point.protocol());

  // wrap it into bredis connection
  r::Connection<next_layer_t> c(std::move(socket));

  return 0;
}
