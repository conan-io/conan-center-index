#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/certify/extensions.hpp>
#include <boost/core/lightweight_test.hpp>

#include <iostream>

int main() {
      boost::asio::io_context ioc{1};
      boost::asio::ssl::context context{boost::asio::ssl::context_base::method::tls_client};
      boost::asio::ssl::stream<boost::asio::ip::tcp::socket> stream(ioc, context);
      constexpr auto hostname = "example.com";

      BOOST_TEST(boost::certify::sni_hostname(stream).empty());
      boost::certify::sni_hostname(stream, hostname);
      BOOST_TEST(boost::certify::sni_hostname(stream) == hostname);
      std::cout << boost::report_errors();

      return 0;
}
