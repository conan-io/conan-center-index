// Minimal consumer used by conan-center-index CI to verify the packaged headers can be found
// and used, and that the transitive ETL dependency is visible.
#include <NinjaHSM/NinjaHSM.hpp>

using namespace NinjaHSM;

namespace {

struct Event {
    int id;
};

class Machine {
public:
    Machine() :
        m_idle(makeState<Event,
            &Machine::idle_entry, &Machine::idle_event, &Machine::idle_exit>("Idle", *this)),
        m_running(makeState<Event,
            &Machine::running_entry, &Machine::running_event, &Machine::running_exit>("Running", *this, &m_idle)),
        m_sm() {
        m_sm.initialTransitionTo(m_idle);
    }

    void step(const Event& event) { m_sm.handleEvent(event); }

private:
    void idle_entry() {}
    void idle_event(const Event& event) {
        if (event.id == 1) {
            m_sm.transitionTo(m_running);
        }
    }
    void idle_exit() {}

    void running_entry() {}
    void running_event(const Event& event) {}
    void running_exit() {}

    State<Event> m_idle;
    State<Event> m_running;
    StateMachine<Event> m_sm;
};

} // namespace

int main() {
    Machine machine;
    Event event{1};
    machine.step(event);
    return 0;
}
