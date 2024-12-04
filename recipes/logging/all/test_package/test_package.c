#include "logging.h"

int main() {
    Logger *logger = newDefaultLogger("testLogger", LOG_DEBUG);

    log_info("This is an info message");
    log_error("This is an error message%s", "123");
    log_fatal("This is an fatal message");
    log_debug("This is a debug message");
    log_warning("This is a warning message%s", "123");

    destroyDefaultLogger();
    return 0;
}
