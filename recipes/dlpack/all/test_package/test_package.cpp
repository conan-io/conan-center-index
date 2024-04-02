#include <dlpack/dlpack.h>
#include <iostream>
#include <cstdlib>

int main()
{
#if DLPACK_VERSION < 60
    int major = (DLPACK_VERSION >> 6) & 7;
    int minor = (DLPACK_VERSION >> 3) & 7;
    int patch = DLPACK_VERSION & 7;
#else
    int major = DLPACK_VERSION / 100;
    int minor = (DLPACK_VERSION - major * 100) / 10;
    int patch = DLPACK_VERSION - major * 100 - minor * 10;
#endif
    std::cout << "dlpack version: " << major << "." << minor << "." << patch << std::endl;
    return EXIT_SUCCESS;
}
