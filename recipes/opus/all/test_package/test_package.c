#include <stdio.h>
#include <opus/opus.h>

int main() {
    int err;
    int rate = 48000;
    int channels = 2;
    int application = OPUS_APPLICATION_AUDIO;
    OpusEncoder *encoder;

    encoder = opus_encoder_create(rate, channels, application, &err);
    opus_encoder_destroy(encoder);
}
