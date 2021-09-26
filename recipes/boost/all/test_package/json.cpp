#include <boost/json.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

using namespace boost::json;

#include <string>
#include <iostream>

int main() {
    object obj;
    obj[ "pi" ] = 3.141;
    obj[ "happy" ] = true;
    obj[ "name" ] = "Boost";
    obj[ "nothing" ] = nullptr;
    obj[ "answer" ].emplace_object()["everything"] = 42;
    obj[ "list" ] = { 1, 0, 2 };
    obj[ "object" ] = { {"currency", "USD"}, {"value", 42.99} };
    std::string s = serialize(obj);
    std::cout << s << '\n';
}
