#include <stdio.h>
#include <speex/speex_resampler.h>

int main(void) {
    int err = 0;
    SpeexResamplerState *state = speex_resampler_init(1, 44100, 48000, 5, &err);
    if (state == NULL || err != RESAMPLER_ERR_SUCCESS) {
        printf("speex_resampler_init failed: %s\n", speex_resampler_strerror(err));
        return 1;
    }
    printf("speexdsp OK\n");
    speex_resampler_destroy(state);
    return 0;
}
