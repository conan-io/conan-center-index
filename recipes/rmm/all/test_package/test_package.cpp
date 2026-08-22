#include <cstdlib>
#include <iostream>
#include <rmm/logger.hpp>
#include <rmm/version_config.hpp>

int main() {
    // The log output will be sent to rmm_log.txt in the build directory by default
    RMM_LOG_INFO("rmm version: {}.{}.{}", RMM_VERSION_MAJOR, RMM_VERSION_MINOR, RMM_VERSION_PATCH);
    return EXIT_SUCCESS;
}
