#include <rotor/asio.hpp>
#include <rotor/thread.hpp>

namespace asio = boost::asio;
namespace pt = boost::posix_time;

struct server_actor : public rotor::actor_base_t {
    using rotor::actor_base_t::actor_base_t;
    void on_start() noexcept override {
        rotor::actor_base_t::on_start();
        std::cout << "hello world\n";
        do_shutdown();
    }
};

int main() {
    asio::io_context io_context;
    auto system_context = rotor::asio::system_context_asio_t::ptr_t{new rotor::asio::system_context_asio_t(io_context)};
    auto strand = std::make_shared<asio::io_context::strand>(io_context);
    auto timeout = boost::posix_time::milliseconds{500};
    auto sup =
        system_context->create_supervisor<rotor::asio::supervisor_asio_t>().strand(strand).timeout(timeout).finish();

    sup->create_actor<server_actor>().timeout(timeout).finish();

    sup->start();
    io_context.run();

    auto thread_context = rotor::thread::system_context_thread_t();

    return 0;
}

