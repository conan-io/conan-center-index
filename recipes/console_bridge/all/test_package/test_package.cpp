#include <cstdlib>

#include <console_bridge/console.h>

int main() {
    console_bridge::setLogLevel(console_bridge::CONSOLE_BRIDGE_LOG_DEBUG);
    CONSOLE_BRIDGE_logInform("CONSOLE_BRIDGE_logInform() ran successfully");
    return EXIT_SUCCESS;
}
