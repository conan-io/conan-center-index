#include <boost/taar/handler/rest.hpp>
#include <boost/taar/handler/rest_arg.hpp>
#include <boost/taar/matcher/method.hpp>
#include <boost/taar/matcher/target.hpp>
#include <boost/taar/session/http.hpp>

#include <boost/json/serialize.hpp>
#include <boost/url/parse.hpp>

#include <iostream>

int add(int a, int b) { return a + b; }

int main()
{
    namespace taar = boost::taar;
    namespace http = boost::beast::http;
    using taar::handler::path_arg;
    using taar::handler::rest;
    using taar::matcher::method;
    using taar::matcher::target;

    taar::session::http session;
    session.register_request_handler(
        method == http::verb::get && target == "/add/{a}/{b}",
        rest(&add, path_arg("a"), path_arg("b")));

    // Touch the compiled Boost.URL and Boost.JSON so the link is tested.
    auto const url = boost::urls::parse_origin_form("/add/2/3");
    std::cout << "boost-taar: " << url->segments().size() << " segments, "
              << boost::json::serialize(boost::json::value {{"sum", add(2, 3)}})
              << '\n';
}
