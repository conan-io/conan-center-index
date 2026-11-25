#include <hsmcpp/hsm.hpp>
#include <hsmcpp/HsmEventDispatcherSTD.hpp>
#include <iostream>
#include <cstdlib>

enum class States : hsmcpp::StateID_t {
    IDLE = 0
};

enum class Events : hsmcpp::EventID_t {
    START = 0
};

int main() {
    auto dispatcher = hsmcpp::HsmEventDispatcherSTD::create();
    dispatcher->stop();
    std::cout << "hsmcpp test_package: HSM created with STD dispatcher successfully" << std::endl;
    return EXIT_SUCCESS;
}
