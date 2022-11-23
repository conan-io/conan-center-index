#include <yder.h>
#include <stdlib.h>

int main() {
    y_init_logs("test_package", Y_LOG_MODE_CONSOLE, Y_LOG_LEVEL_DEBUG, NULL, "Logging started");
    y_log_message(Y_LOG_LEVEL_INFO, "We started");
    y_log_message(Y_LOG_LEVEL_DEBUG, "Are we really?");
    y_log_message(Y_LOG_LEVEL_WARNING, "We have nothing to do!");
    y_log_message(Y_LOG_LEVEL_ERROR, "Oops!");
    y_log_message(Y_LOG_LEVEL_INFO, "Bye then!");
    y_close_logs();
    return 0;
}
