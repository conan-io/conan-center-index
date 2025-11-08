#include <iostream>
#include <string>
#include <unilink/unilink.hpp>

int main() {
    std::cout << "Testing unilink package..." << std::endl;

    // Exercise a compiled symbol to ensure the library links properly
    auto& logger = unilink::common::Logger::instance();
    logger.set_enabled(true);
    logger.set_console_output(false);
    logger.set_level(unilink::common::LogLevel::INFO);
    logger.log(unilink::common::LogLevel::INFO, "test_package", "basic_log", "unilink log test");
    logger.flush();

    std::cout << "unilink runtime test passed!" << std::endl;
    return 0;
}
