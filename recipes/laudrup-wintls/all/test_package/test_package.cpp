#include <boost/asio.hpp>
#include <boost/wintls.hpp>

namespace net = boost::asio;
namespace ssl = boost::wintls;

int main(int argc, char **argv) {
  net::io_context ioc;
  ssl::context ctx{boost::wintls::method::system_default};
  ctx.use_default_certificates(true);
  ctx.verify_server_certificate(true);
  ioc.run();

  return 0;
}
