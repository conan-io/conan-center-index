#include <mapbox/variant.hpp>
#include <mapbox/variant_io.hpp>

#include <iostream>
#include <string>

int main() {
    typedef mapbox::util::variant<double, std::string> variant_type;
    variant_type v0(3.14159);
    variant_type v1(std::string("3.14159"));
    std::cout << "v0: " << v0 << " v1: " << v1 << std::endl;
    return 0;
}
