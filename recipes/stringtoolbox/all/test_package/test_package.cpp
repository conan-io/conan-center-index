#include "stringtoolbox.hpp"

#include <iostream>

int main() {
    std::string target = "  ABC ";

    std::cout << target << std::endl;

    stringtoolbox::trim(target);

    std::cout << target << std::endl;

    return 0;
}
