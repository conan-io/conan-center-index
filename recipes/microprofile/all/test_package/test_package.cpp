#include <iostream>

#include <microprofile/microprofile.h>

int main() {
#if MICROPROFILE_ENABLED
    MicroProfileInit();
    std::cout << "Microprofile successfully initialized." << std::endl;
#endif
    std::cout << "Tick = " << MicroProfileTick() << std::endl;
    return 0;
}
