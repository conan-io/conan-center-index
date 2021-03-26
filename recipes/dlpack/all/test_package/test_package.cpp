#include <dlpack/dlpack.h>
#include <iostream>
#include <cstdlib>

int main()
{
    int major = (DLPACK_VERSION >> 6) & 7;
    int minor = (DLPACK_VERSION >> 3) & 7;
    int patch = DLPACK_VERSION & 7;
    std::cout << "dlpack version: " << major << "." << minor << "." << patch << std::endl;
    return EXIT_SUCCESS;
}
