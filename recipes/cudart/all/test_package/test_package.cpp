#include <cuda_runtime_api.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int runtimeVersion = 0, driverVersion = 0;
    cudaError_t status = cudaRuntimeGetVersion(&runtimeVersion);
    printf("runtime version available: %d (status %d: \"%s\")\n", runtimeVersion, status, cudaGetErrorString(status));
    status = cudaDriverGetVersion(&driverVersion);
    printf("driver version available: %d (status %d: \"%s\")\n", runtimeVersion, status, cudaGetErrorString(status));
    return EXIT_SUCCESS;
}