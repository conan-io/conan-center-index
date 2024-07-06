#include <libavutil/hwcontext.h>

#include <stdio.h>
#include <stdlib.h>

int main()
{
    enum AVHWDeviceType foo = AV_HWDEVICE_TYPE_VULKAN;
    printf("test: %s", av_hwdevice_get_type_name(foo));
    return EXIT_SUCCESS;
}
