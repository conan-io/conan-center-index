#include <stdio.h>
#include <stdlib.h>
#include <speex/speex_resampler.h>

int main(void) {
    int err;
    SpeexResamplerState *resampler = speex_resampler_init(1, 8000, 16000, 5, &err);
    if (resampler == NULL || err != RESAMPLER_ERR_SUCCESS) {
        fprintf(stderr, "Failed to create resampler: %d\n", err);
        return EXIT_FAILURE;
    }
    printf("SpeexDSP resampler created successfully\n");
    speex_resampler_destroy(resampler);
    return EXIT_SUCCESS;
}
