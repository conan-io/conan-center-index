#include <iostream>
#include "polyxml.hpp"

int main() {
    auto schema = polyxml::SchemaBuilder("Root")
        .add_attribute("id", "id", POLYXML_SCALAR_STRING)
        .build();
    std::cout << "PolyXML Conan test package verified successfully!" << std::endl;
    return 0;
}
