#include <tracy/Tracy.hpp>
#include <iostream>

int main(int argc, char **argv) {
    #ifdef MANUAL_LIFETIME
    tracy::StartupProfiler();
    #endif

    std::cout << "TracyIsStarted: " << TracyIsStarted << std::endl;
    {
        // The ZoneScoped removes its profiler when it goes out of scope.
        // Ensure this happens before the profiler is shutdown.
        ZoneScopedN("main");
    }
    #ifdef MANUAL_LIFETIME
    tracy::ShutdownProfiler();
    #endif



    return 0;
}
