#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavfilter/avfilter.h>
#include <libavdevice/avdevice.h>
#include <libswresample/swresample.h>
#include <libswscale/swscale.h>
#include <libavutil/hwcontext.h>

#include <stdio.h>

int main() {
    avcodec_register_all();
    av_register_all();
    avfilter_register_all();
    avdevice_register_all();
    swresample_version();
    swscale_version();
    if (avcodec_find_encoder_by_name("libx264") == NULL) {
        printf("Unable to find libx264 encoder\n");
        return -1;
    }
    return 0;
}
