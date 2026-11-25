#include <hsmcpp/hsm.hpp>
#include <hsmcpp/HsmEventDispatcherSTD.hpp>
#include <iostream>
#include <cstdlib>

int main() {
    auto dispatcher = hsmcpp::HsmEventDispatcherSTD::create();
    dispatcher->stop();
    std::cout << "hsmcpp test_package: HSM created with STD dispatcher successfully" << std::endl;
    return EXIT_SUCCESS;
}
