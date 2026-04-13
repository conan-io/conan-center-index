#include "lunar_log.hpp"
#include <lunar_log/macros.hpp>

int main() {
    auto logger = minta::LunarLog::configure()
        .writeTo<minta::ConsoleSink>("console")
        .build();

    logger.info("Test-name {name}", "name", "alice");
    return 0;
}
