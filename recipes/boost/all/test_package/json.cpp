#include <boost/json.hpp>

int main() {
    boost::json::object obj;
    obj[ "pi" ] = 3.141;
    std::string s = serialize(obj);
    return 0;
}
