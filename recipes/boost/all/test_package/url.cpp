#include <boost/url.hpp>

int main() {
    boost::urls::url u("https://www.example.com");
    u.scheme();
    return 0;
}
