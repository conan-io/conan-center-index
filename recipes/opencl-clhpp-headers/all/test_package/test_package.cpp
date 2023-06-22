#define CL_HPP_MINIMUM_OPENCL_VERSION 120
#define CL_HPP_TARGET_OPENCL_VERSION 120

#include <CL/opencl.hpp>

#include <cstdlib>
#include <iostream>

int main() {
    cl::Context context;
    cl::Device device_id;

    (void) context;
    (void) device_id;

    if (CL_VERSION_1_2 != 1) {
        std::cerr << "Wrong OpenCL header version";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
