#include <cstdlib>
#include <iostream>
#include <vector>

#include <embree3/rtcore.h>
RTC_NAMESPACE_OPEN

#include <immintrin.h>

#if !defined(_MM_SET_DENORMALS_ZERO_MODE)
#define _MM_DENORMALS_ZERO_ON (0x0040)
#define _MM_DENORMALS_ZERO_OFF (0x0000)
#define _MM_DENORMALS_ZERO_MASK (0x0040)
#define _MM_SET_DENORMALS_ZERO_MODE(x)                                         \
    (_mm_setcsr((_mm_getcsr() & ~_MM_DENORMALS_ZERO_MASK) | (x)))
#endif

int main(int p_arg_count, char **p_arg_vector) {
    std::cout << "'Embree package test (compilation, linking, and execution)."
              << std::endl;

    _MM_SET_FLUSH_ZERO_MODE(_MM_FLUSH_ZERO_ON);
    _MM_SET_DENORMALS_ZERO_MODE(_MM_DENORMALS_ZERO_ON);

    std::cout << "Creating a new Embree device ..." << std::endl;
    RTCDevice device = rtcNewDevice("verbose=1");
    std::cout << "Releasing the Embree device ..." << std::endl;
    rtcReleaseDevice(device);

    std::cout << "'Embree package works!" << std::endl;
    return EXIT_SUCCESS;
}
