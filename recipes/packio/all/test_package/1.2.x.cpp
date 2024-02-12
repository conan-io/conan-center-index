#include <optional> // missing include in recent versions of MSVC

#include <packio/packio.h>

#if defined(PACKIO_STANDALONE_ASIO)
namespace net = ::asio;
#else // defined(PACKIO_STANDALONE_ASIO)
namespace net = ::boost::asio;
#endif // defined(PACKIO_STANDALONE_ASIO)

int main(int, char **) {
  net::io_context io;

  net::ip::tcp::endpoint bind_ep{net::ip::make_address("127.0.0.1"), 0};
  auto server = packio::make_server(net::ip::tcp::acceptor{io, bind_ep});
  auto client = packio::make_client(net::ip::tcp::socket{io});

  return 0;
}
