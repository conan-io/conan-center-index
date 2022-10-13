#include <iostream>

#include "mp++/integer.hpp"
#include "mp++/rational.hpp"

int main() {
    auto integer = mppp::integer<2>{4};
    std::cout << integer << std::endl;

    auto rational = mppp::rational<2>{4};
    std::cout << rational << std::endl;

    return 0;
}
