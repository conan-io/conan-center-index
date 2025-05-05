#include <rotor/supervisor.h>
#include <iostream>


namespace {
namespace to {
struct on_timer_trigger {};
} // namespace to
} // namespace

namespace rotor {
template <>
inline auto rotor::actor_base_t::access<to::on_timer_trigger, request_id_t, bool>(request_id_t request_id,
                                                                                  bool cancelled) noexcept {
    on_timer_trigger(request_id, cancelled);
}
} // namespace rotor

struct dummy_supervisor_t : public rotor::supervisor_t {
    using rotor::supervisor_t::supervisor_t;
    using timers_map_t = std::unordered_map<rotor::request_id_t, rotor::timer_handler_base_t *>;

    timers_map_t timers_map;

    void do_start_timer(const rotor::pt::time_duration &, rotor::timer_handler_base_t &handler) noexcept override {
        timers_map.emplace(handler.request_id, &handler);
    }

    void do_cancel_timer(rotor::request_id_t timer_id) noexcept override {
        auto it = timers_map.find(timer_id);
        auto &actor_ptr = it->second->owner;
        actor_ptr->access<to::on_timer_trigger, rotor::request_id_t, bool>(timer_id, true);
        timers_map.erase(it);
    }

    void start() noexcept override {}
    void shutdown() noexcept override {}
    void enqueue(rotor::message_ptr_t) noexcept override {}
};

struct hello_actor : public rotor::actor_base_t {
    using rotor::actor_base_t::actor_base_t;
    void on_start() noexcept override {
        rotor::actor_base_t::on_start();
        std::cout << "hello world\n";
        supervisor->do_shutdown();
    }
};

int main() {
    rotor::system_context_t ctx{};
    auto timeout = boost::posix_time::milliseconds{500}; /* does not matter */
    auto sup = ctx.create_supervisor<dummy_supervisor_t>().timeout(timeout).finish();
    sup->create_actor<hello_actor>().timeout(timeout).finish();
    sup->do_process();
    return 0;
}

