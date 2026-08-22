#include <boost/regex.hpp>

int main() {
    boost::regex pat("\\w+");
    boost::regex_match("test", pat);
    return 0;
}
