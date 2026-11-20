#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <akasha.hpp>

int main() {
    akasha::Store store;
    const akasha::Status last_status{store.last_status()};
    std::cout << "Akasha Last status: " << static_cast<int>(last_status) << std::endl;
    std::cout << "Akasha version: " << akasha::version() << std::endl;
    return EXIT_SUCCESS;
}
