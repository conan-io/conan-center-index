#include <cstdlib>
#include <iostream>
#include <valijson/validator.hpp>


int main() {
    std::cout << "Conan Test package - valijson: " << valijson::utils::u8_strlen("Conan") << std::endl;
    return EXIT_SUCCESS;
}
