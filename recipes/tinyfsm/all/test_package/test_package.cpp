#include <tinyfsm.hpp>
#include <iostream>

struct ToggleEvent : tinyfsm::Event {};

class TestFsm : public tinyfsm::Fsm<TestFsm>
{
public:
    void react(ToggleEvent const &) {
        std::cout << "Event received" << std::endl;
    }

    virtual void entry() {
        std::cout << "State entered" << std::endl;
    }
};

// Initialize state
using fsm_handle = TestFsm;
FSM_INITIAL_STATE(TestFsm, TestFsm)

int main()
{
    std::cout << "Testing tinyfsm package..." << std::endl;

    // Start the state machine
    fsm_handle::start();

    // Send an event
    fsm_handle::dispatch(ToggleEvent());

    std::cout << "tinyfsm package test completed successfully!" << std::endl;
    return 0;
}
