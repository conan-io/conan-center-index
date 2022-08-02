#include <cstdlib>
#include "spdlog/spdlog.h"

int main(void) {
    spdlog::info("Welcome to spdlog version {}.{}.{}  !", SPDLOG_VER_MAJOR, SPDLOG_VER_MINOR, SPDLOG_VER_PATCH);
    return EXIT_SUCCESS;
}
