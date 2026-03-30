#include <akasha.hpp>
#include <iostream>

int main() {
    akasha::Store store;
    std::cout << "Akasha version: " << akasha::version() << std::endl;
    (void) store.clear();
    return 0;
}
