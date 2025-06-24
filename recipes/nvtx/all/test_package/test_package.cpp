#include <stdlib.h>
#include <nvtx3/nvtx3.hpp>

int main()
{
    nvtxInitialize(NULL);
    nvtxRangeId_t main_range = nvtxRangeStartA("main");
    nvtxRangeEnd(main_range);
    return EXIT_SUCCESS;
}