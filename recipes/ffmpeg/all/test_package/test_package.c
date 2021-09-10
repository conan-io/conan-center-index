#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavfilter/avfilter.h>
#include <libavdevice/avdevice.h>
#include <libswresample/swresample.h>
#include <libswscale/swscale.h>
#include <libavutil/hwcontext.h>

#include <stdio.h>

int main() {
    avdevice_register_all();

    printf("configuration: %s\n", avcodec_configuration());

    printf("avcodec version: %d.%d.%d\n", AV_VERSION_MAJOR(avcodec_version()), AV_VERSION_MINOR(avcodec_version()), AV_VERSION_MICRO(avcodec_version()));
    printf("avfilter version: %d.%d.%d\n", AV_VERSION_MAJOR(avfilter_version()), AV_VERSION_MINOR(avfilter_version()), AV_VERSION_MICRO(avfilter_version()));
    printf("avdevice version: %d.%d.%d\n", AV_VERSION_MAJOR(avdevice_version()), AV_VERSION_MINOR(avdevice_version()), AV_VERSION_MICRO(avdevice_version()));
    printf("swresample version: %d.%d.%d\n", AV_VERSION_MAJOR(swresample_version()), AV_VERSION_MINOR(swresample_version()), AV_VERSION_MICRO(swresample_version()));
    printf("swscale version: %d.%d.%d\n", AV_VERSION_MAJOR(swscale_version()), AV_VERSION_MINOR(swscale_version()), AV_VERSION_MICRO(swscale_version()));

    if (avcodec_find_encoder_by_name("rawvideo") == NULL) {
        printf("Unable to find rawvideo encoder\n");
        return -1;
    }
    return 0;
}
