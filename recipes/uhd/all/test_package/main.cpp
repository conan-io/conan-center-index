#include <uhd/version.hpp>
#include <iostream>

int main() {
    std::cout << "UHD version: " << uhd::get_version_string() << std::endl;
    std::cout << "UHD ABI: " << uhd::get_abi_string() << std::endl;
    return 0;
}
