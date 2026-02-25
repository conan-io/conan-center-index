#include <lunar_log/lunar_log.hpp>
#include <iostream>

int main() {
    auto logger = lunar_log::LoggerConfiguration()
        .writeTo().console()
        .createLogger();

    logger->information("Hello from LunarLog {Version}", "1.29.1");
    std::cout << "LunarLog test_package OK" << std::endl;
    return 0;
}
