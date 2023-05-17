#include <stdint.h>
#include "x264.h"

#include <stdlib.h>

int main()
{
    x264_param_t preset;
    x264_t *encoder;
    x264_param_default_preset(&preset, "ultrafast", "zerolatency");
    preset.i_width = 640;
    preset.i_height = 480;
    encoder = x264_encoder_open(&preset);
    x264_encoder_close(encoder);
    return EXIT_SUCCESS;
}
