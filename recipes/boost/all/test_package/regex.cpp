#include <boost/regex.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main() {
    boost::regex pat("\\w+");
    boost::regex_match("test", pat);
    return 0;
}
