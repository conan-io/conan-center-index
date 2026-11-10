#include <libavutil/hwcontext.h>

int main(void)
{
    /* Pull in the hardware-context implementations without requiring a GPU. */
    av_hwdevice_iterate_types(AV_HWDEVICE_TYPE_NONE);
    return 0;
}
