#include <stdlib.h>
#include <nvtx3/nvToolsExt.h>

int main()
{
    nvtxInitialize(NULL);
    nvtxRangeId_t main_range = nvtxRangeStartA("main");
    nvtxRangeEnd(main_range);
    return EXIT_SUCCESS;
}
