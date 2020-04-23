#include <packio/packio.h>

namespace ip = boost::asio::ip;

int main(int, char **) {
  boost::asio::io_context io;

  ip::tcp::endpoint bind_ep{ip::make_address("127.0.0.1"), 0};
  auto server = packio::make_server(ip::tcp::acceptor{io, bind_ep});
  auto client = packio::make_client(ip::tcp::socket{io});

  return 0;
}
