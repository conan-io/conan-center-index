#include <boost/url.hpp>
#include <iostream>

int main() {
    BOOST_NAMESPACE::urls::url u("https://www.example.com");
    std::cout << "Testing Boost::URL: " << u.scheme() << std::endl;
    return 0;
}
