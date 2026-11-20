#include <hsmcpp/hsm.hpp>
#include <hsmcpp/HsmEventDispatcherSTD.hpp>
#include <cstdio>

enum class States : hsmcpp::StateID_t {
    IDLE = 0
};

enum class Events : hsmcpp::EventID_t {
    START = 0
};

int main() {
    // Create STD dispatcher
    auto dispatcher = hsmcpp::HsmEventDispatcherSTD::create();

    // Create HSM with initial state
    hsmcpp::HierarchicalStateMachine hsm(static_cast<hsmcpp::StateID_t>(States::IDLE));
    hsm.registerState(static_cast<hsmcpp::StateID_t>(States::IDLE));

    printf("hsmcpp test_package: HSM created with STD dispatcher successfully\n");
    return 0;
}
