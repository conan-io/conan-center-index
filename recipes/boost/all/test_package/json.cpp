#include <boost/json.hpp>
#include <iostream>

int main() {
    BOOST_NAMESPACE::json::object obj;
    obj[ "pi" ] = 3.141;
    std::string s = serialize(obj);
    std::cout << "Testing Boost::JSON: " << s << std::endl;
    return 0;
}
