#include <stdiobus/version.hpp>
#include <iostream>

int main() {
    std::cout << "stdiobus version: " << stdiobus::version() << std::endl;
    std::cout << "kernel compatible: " << std::boolalpha << stdiobus::kernel_compatible() << std::endl;
    return stdiobus::version_major() == 1 ? 0 : 1;
}
