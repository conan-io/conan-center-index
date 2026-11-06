#include <sioxx/sioxx.hpp>

int main()
{
    sioxx::client_options opts;
    opts.parser = sioxx::parser_kind::msgpack;
    opts.reconnect_attempts = 5;
    opts.reconnect_delay = std::chrono::milliseconds(1000);
    opts.reconnect_delay_max = std::chrono::milliseconds(30000);
    opts.reconnect_randomization_factor = 0.5;

    sioxx::client client(opts);

    auto sock = client.socket("/chat");
    sock->on("hello_world", [](const std::string &event, sioxx::message data) {});

    const auto message = sioxx::make_args("conan", 2);
    return message.size() == 2 ? 0 : 1;
}
