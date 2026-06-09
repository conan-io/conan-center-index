#include <alpaka/alpaka.hpp>

#include <iostream>

int main() {
    std::cout << "alpaka version: "
              << ALPAKA_VERSION_MAJOR << "."
              << ALPAKA_VERSION_MINOR << "."
              << ALPAKA_VERSION_PATCH << std::endl;

    // List enabled accelerator tags
    std::cout << "Enabled accelerator tags:" << std::endl;
    alpaka::printTagNames<alpaka::EnabledAccTags>();

    return 0;
}

