#include <stdio.h>

#include <tinyalsa/pcm.h>

int main(void)
{
    printf("TinyALSA test_package\n");

    unsigned int card = 0;
    unsigned int device = 0;
    int flags = PCM_IN;

    const struct pcm_config config = {
        .channels = 2,
        .rate = 48000,
        .format = PCM_FORMAT_S32_LE,
        .period_size = 1024,
        .period_count = 2,
        .start_threshold = 1024,
        .silence_threshold = 1024 * 2,
        .stop_threshold = 1024 * 2
    };

    struct pcm *pcm = pcm_open(card, device, flags, &config);
    pcm_close(pcm);

    return 0;
}
