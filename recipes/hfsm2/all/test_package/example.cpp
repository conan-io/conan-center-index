#include <assert.h>
#include <hfsm2/machine.hpp>

struct Context {
    bool on = false;
};

using Config = hfsm2::Config
                    ::ContextT<Context&>;

using M = hfsm2::MachineT<Config>;

using FSM = M::PeerRoot<
                struct Off,
                struct On
            >;

struct Off
    : FSM::State
{
    void enter(PlanControl& control) {
        control.context().on = false;
    }
};

struct On
    : FSM::State
{
    void enter(PlanControl& control) {
        control.context().on = true;
    }
};

int
main() {
    Context context;
    FSM::Instance machine{context};

    machine.changeTo<On>();
    machine.update();

    assert(context.on == true);

    return 0;
}