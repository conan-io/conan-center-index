#include <boost/json.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main() {
    boost::json::object obj;
    obj[ "pi" ] = 3.141;
    std::string s = serialize(obj);
    return 0;
}
