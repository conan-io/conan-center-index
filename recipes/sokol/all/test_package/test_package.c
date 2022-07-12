#define SOKOL_IMPL
#include "sokol_time.h"

int main()
{
    stm_setup();
    uint64_t time_now = stm_now();
    double seconds = stm_sec(time_now);
    return 0;
}
