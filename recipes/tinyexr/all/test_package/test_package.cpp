#include <iostream>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#endif

#define TINYEXR_IMPLEMENTATION
#include "tinyexr.h"

int main(int argc, const char *argv[])
{
    float* out;
    int width;
    int height;
    const char* err = nullptr;

    int ret = LoadEXR(&out, &width, &height, "non-real-file.exr", &err);

    if (ret != TINYEXR_SUCCESS) {
        std::cout << "Test message\n"; // Always prints
    }

    return 0;
}
