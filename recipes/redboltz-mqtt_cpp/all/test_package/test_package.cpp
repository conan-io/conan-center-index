#include <mqtt_client_cpp.hpp>

int main() {
    MQTT_NS::setup_log();

    boost::asio::io_context ioc;

    auto c = MQTT_NS::make_async_client(ioc, "localhost", "40000");
    
    c->set_client_id("test_package");
    c->set_clean_session(true);

    return 0;
}
