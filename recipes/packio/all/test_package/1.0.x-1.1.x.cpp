#include <optional> // missing include in recent versions of MSVC

#include <packio/packio.h>

namespace ip = boost::asio::ip;

int main(int, char **) {
  boost::asio::io_context io;

  ip::tcp::endpoint bind_ep{ip::make_address("127.0.0.1"), 0};
  auto server =
      std::make_shared<packio::server<ip::tcp>>(ip::tcp::acceptor{io, bind_ep});
  auto client = std::make_shared<packio::client<ip::tcp>>(ip::tcp::socket{io});

  return 0;
}
