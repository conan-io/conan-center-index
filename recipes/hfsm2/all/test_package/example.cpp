#include <cstdlib>
#include <iostream>
#include <hfsm2/machine.hpp>

struct Context{};

using Config = hfsm2::Config::ContextT<Context&>;
using M = hfsm2::MachineT<Config>;
using FSM = M::PeerRoot<struct State>;

struct State : FSM::State {};


int main(void) {
    Context context;
    FSM::Instance machine{context};
    machine.update();
    std::cout << "[HFSM2] Test package passed with success." << std::endl;
    return EXIT_SUCCESS;
}
