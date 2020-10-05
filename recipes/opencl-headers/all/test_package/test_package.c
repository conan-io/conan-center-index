#define CL_TARGET_OPENCL_VERSION 220
#include <CL/opencl.h>

#include <stdlib.h>
#include <stdio.h>

int main() {
    cl_context context;
    cl_device_id device_id;

    (void) context;
    (void) device_id;

    if (CL_VERSION_2_2 != 1) {
        puts("Wrong OpenCL header version");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
