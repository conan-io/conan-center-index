#include <cstdlib>
#include "spdlog/spdlog.h"

#if __has_include("spdlog/fmt/bundled/core.h")
   #error "bundled fmt within spdlog should not be present"
#endif

int main(void) {
    spdlog::info("Welcome to spdlog version {}.{}.{}  !", SPDLOG_VER_MAJOR, SPDLOG_VER_MINOR, SPDLOG_VER_PATCH);
    return EXIT_SUCCESS;
}
