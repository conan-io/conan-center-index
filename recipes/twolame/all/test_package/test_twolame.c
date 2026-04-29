/* Minimal test: init encoder, set params, encode silence, close */
#include <twolame.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    twolame_options *opts = twolame_init();
    if (!opts) {
        fprintf(stderr, "FAIL: twolame_init() returned NULL\n");
        return 1;
    }

    twolame_set_in_samplerate(opts, 44100);
    twolame_set_out_samplerate(opts, 44100);
    twolame_set_bitrate(opts, 192);
    twolame_set_num_channels(opts, 2);
    twolame_set_mode(opts, TWOLAME_STEREO);

    if (twolame_init_params(opts) != 0) {
        fprintf(stderr, "FAIL: twolame_init_params() failed\n");
        twolame_close(&opts);
        return 1;
    }

    /* Encode one frame of silence */
    short pcm[TWOLAME_SAMPLES_PER_FRAME * 2];
    memset(pcm, 0, sizeof(pcm));

    unsigned char mp2buf[16384];
    int ret = twolame_encode_buffer_interleaved(opts, pcm,
                                                 TWOLAME_SAMPLES_PER_FRAME,
                                                 mp2buf, sizeof(mp2buf));
    if (ret < 0) {
        fprintf(stderr, "FAIL: twolame_encode_buffer_interleaved() returned %d\n", ret);
        twolame_close(&opts);
        return 1;
    }

    /* Also test the float32_interleaved variant (the one with the TL_API fix) */
    float fpcm[TWOLAME_SAMPLES_PER_FRAME * 2];
    memset(fpcm, 0, sizeof(fpcm));

    ret = twolame_encode_buffer_float32_interleaved(opts, fpcm,
                                                     TWOLAME_SAMPLES_PER_FRAME,
                                                     mp2buf, sizeof(mp2buf));
    if (ret < 0) {
        fprintf(stderr, "FAIL: twolame_encode_buffer_float32_interleaved() returned %d\n", ret);
        twolame_close(&opts);
        return 1;
    }

    twolame_close(&opts);

    printf("twolame %s: all tests passed\n", get_twolame_version());
    return 0;
}
