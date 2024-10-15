#include <cstdlib>
#include <iostream>
#include "arm_compute/core/Version.h"


int main(void) {
    std::cout << "ComputeLibrary information:" << std::endl;
    std::cout << arm_compute::build_information() << std::endl;

    return EXIT_SUCCESS;
}
