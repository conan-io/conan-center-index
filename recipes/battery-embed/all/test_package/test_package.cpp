#include <cstdlib>
#include <iostream>
#include <cstdint>

#include "battery/embed.hpp"

int main(void) {
    std::cout << b::embed<"test_package.cpp">() << std::endl;
    return EXIT_SUCCESS;
}
