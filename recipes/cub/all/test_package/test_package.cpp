#include <cstdlib>
#include <iostream>
#include <cub/version.cuh>

int main() {
    std::cout << "CUB version: " <<
        CUB_MAJOR_VERSION << "." << CUB_MINOR_VERSION << "." << CUB_SUBMINOR_VERSION << std::endl;
    return EXIT_SUCCESS;
}
