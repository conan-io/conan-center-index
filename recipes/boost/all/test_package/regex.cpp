#include <boost/regex.hpp>

int main() {
    BOOST_NAMESPACE::regex pat("\\w+");
    BOOST_NAMESPACE::regex_match("test", pat);
    return 0;
}
