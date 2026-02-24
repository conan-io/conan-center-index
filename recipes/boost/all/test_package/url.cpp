#include <boost/url.hpp>
#include <iostream>

int main() {
    boost::urls::url u("https://www.example.com");
    std::cout << "Testing Boost::URL: " << u.scheme() << std::endl;
    return 0;
}
