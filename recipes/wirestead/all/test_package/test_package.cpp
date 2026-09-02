#include <iostream>
#include <string>
#include <wirestead/wirestead.hpp>

int main() {
    std::cout << "Testing wirestead package..." << std::endl;

    // Exercise a compiled symbol to ensure the library links properly
    auto& logger = wirestead::diagnostics::Logger::instance();
    logger.set_enabled(true);
    logger.set_console_output(false);
    logger.set_level(wirestead::diagnostics::LogLevel::INFO);
    logger.log(wirestead::diagnostics::LogLevel::INFO, "test_package", "basic_log", "wirestead log test");
    logger.flush();

    std::cout << "wirestead runtime test passed!" << std::endl;
    return 0;
}
