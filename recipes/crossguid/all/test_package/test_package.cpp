#include <iostream>

#include "Guid.hpp"

int main(void) {
    auto const g = xg::newGuid();

    std::cout << "Here is a guid: " << g << std::endl;

    return 0;
}
