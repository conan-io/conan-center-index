#include <iostream>
#include <string>
#include <unilink/unilink.hpp>

int main() {
    std::cout << "Testing unilink package..." << std::endl;

    // Exercise a compiled symbol to ensure the library links properly
    auto& logger = unilink::diagnostics::Logger::instance();
    logger.set_enabled(true);
    logger.set_console_output(false);
    logger.set_level(unilink::diagnostics::LogLevel::INFO);
    logger.log(unilink::diagnostics::LogLevel::INFO, "test_package", "basic_log", "unilink log test");
    logger.flush();

    std::cout << "unilink runtime test passed!" << std::endl;
    return 0;
}
