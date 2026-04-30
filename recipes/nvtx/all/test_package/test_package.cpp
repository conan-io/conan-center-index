#include <stdlib.h>

#ifdef OLD_COMPAT
#include <nvtx3/nvToolsExt.h>
#else
#include <nvtx3/nvtx3.hpp>
#endif

int main()
{
    nvtxInitialize(NULL);

#ifndef OLD_COMPAT
    NVTX3_FUNC_RANGE();
#endif

    nvtxRangeId_t main_range = nvtxRangeStartA("main");
    nvtxRangeEnd(main_range);
    return EXIT_SUCCESS;
}