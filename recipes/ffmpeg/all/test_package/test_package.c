#ifdef HAVE_FFMPEG_AVCODEC
#   include <libavcodec/avcodec.h>
#endif
#ifdef HAVE_FFMPEG_AVFORMAT
#   include <libavformat/avformat.h>
#endif
#ifdef HAVE_FFMPEG_AVFILTER
#   include <libavfilter/avfilter.h>
#endif
#ifdef HAVE_FFMPEG_AVDEVICE
#   include <libavdevice/avdevice.h>
#endif
#ifdef HAVE_FFMPEG_SWRESAMPLE
#   include <libswresample/swresample.h>
#endif
#ifdef HAVE_FFMPEG_SWSCALE
#   include <libswscale/swscale.h>
#endif
#include <libavutil/hwcontext.h>

#include <stdio.h>
#include <stdlib.h>

int main()
{
    #ifdef HAVE_FFMPEG_AVCODEC
        printf("configuration: %s\n", avcodec_configuration());
        printf("avcodec version: %d.%d.%d\n", AV_VERSION_MAJOR(avcodec_version()), AV_VERSION_MINOR(avcodec_version()), AV_VERSION_MICRO(avcodec_version()));
    #else
        printf("avcodec is disabled!\n");
    #endif
    #ifdef HAVE_FFMPEG_AVFILTER
        printf("avfilter version: %d.%d.%d\n", AV_VERSION_MAJOR(avfilter_version()), AV_VERSION_MINOR(avfilter_version()), AV_VERSION_MICRO(avfilter_version()));
    #else
        printf("avfilter is disabled!\n");
    #endif
    #ifdef HAVE_FFMPEG_AVDEVICE
        avdevice_register_all();
        printf("avdevice version: %d.%d.%d\n", AV_VERSION_MAJOR(avdevice_version()), AV_VERSION_MINOR(avdevice_version()), AV_VERSION_MICRO(avdevice_version()));
    #else
        printf("avdevice is disabled!\n");
    #endif
    #ifdef HAVE_FFMPEG_SWRESAMPLE
        printf("swresample version: %d.%d.%d\n", AV_VERSION_MAJOR(swresample_version()), AV_VERSION_MINOR(swresample_version()), AV_VERSION_MICRO(swresample_version()));
    #else
        printf("swresample is disabled!\n");
    #endif
    #ifdef HAVE_FFMPEG_SWSCALE
        printf("swscale version: %d.%d.%d\n", AV_VERSION_MAJOR(swscale_version()), AV_VERSION_MINOR(swscale_version()), AV_VERSION_MICRO(swscale_version()));
    #else
        printf("swscale is disabled!\n");
    #endif

    return EXIT_SUCCESS;
}
