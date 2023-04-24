#include <dlpack/dlpack.h>
#include <iostream>
#include <cstdlib>

int main()
{
    int major, minor, patch;
    if (DLPACK_VERSION < 48) {
        major = (DLPACK_VERSION >> 6) & 7;
        minor = (DLPACK_VERSION >> 3) & 7;
        patch = DLPACK_VERSION & 7;
    } else {
        major = 0;
        minor = DLPACK_VERSION / 10;
        patch = DLPACK_VERSION % 10;
    }
    std::cout << "dlpack version: " << major << "." << minor << "." << patch << std::endl;
    return EXIT_SUCCESS;
}
