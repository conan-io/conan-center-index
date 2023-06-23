#include <iostream>

#include <plog/Log.h>
#ifdef PLOG_EXPLICIT_INIT
#  include <plog/Initializers/RollingFileInitializer.h>
#endif

int main() {
    plog::init(plog::debug, "log.txt");
    PLOG(plog::info) << "Hello world!";
    return 0;
}

