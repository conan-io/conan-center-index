#include <packio/packio.h>

namespace net = packio::net;

int main(int, char **) {
  net::io_context io;

  net::ip::tcp::endpoint bind_ep{net::ip::make_address("127.0.0.1"), 0};
  auto msgpack_server =
      packio::msgpack_rpc::make_server(net::ip::tcp::acceptor{io, bind_ep});
  auto msgpack_client =
      packio::msgpack_rpc::make_client(net::ip::tcp::socket{io});
  auto json_server =
      packio::nl_json_rpc::make_server(net::ip::tcp::acceptor{io, bind_ep});
  auto json_client = packio::nl_json_rpc::make_client(net::ip::tcp::socket{io});

  return 0;
}
