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
    if (argc < 2) {
        std::cerr << "Need at least one argument\n";
    }

    float* out;
    int width;
    int height;
    const char* err = nullptr;

    int ret = LoadEXR(&out, &width, &height, argv[1], &err);

    if (ret == TINYEXR_SUCCESS) {
        free(out);
    } else {
        if(err) {
            std::cerr << err << std::endl;
        } else {
            std::cerr << "Unknown error." << std::endl;
        }
    }

    return 0;
}
