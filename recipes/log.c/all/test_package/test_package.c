#include <log.h>

int main() {
    log_trace("Hello %s", "world");
    log_trace(log_level_string(0));
    return 0;
}
