
// This test_package has been taken from examples/pcm-readi.c

#include <stdio.h>
#include <stdlib.h>

#include <tinyalsa/pcm.h>

static size_t read_frames(void **frames)
{
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
    if (pcm == NULL) {
        fprintf(stderr, "failed to allocate memory for PCM\n");
        return 0;
    } else if (!pcm_is_ready(pcm)){
        pcm_close(pcm);
        fprintf(stderr, "failed to open PCM\n");
        return 0;
    }

    unsigned int frame_size = pcm_frames_to_bytes(pcm, 1);
    unsigned int frames_per_sec = pcm_get_rate(pcm);

    *frames = malloc(frame_size * frames_per_sec);
    if (*frames == NULL) {
        fprintf(stderr, "failed to allocate frames\n");
        pcm_close(pcm);
        return 0;
    }

    int read_count = pcm_readi(pcm, *frames, frames_per_sec);

    size_t byte_count = pcm_frames_to_bytes(pcm, read_count);

    pcm_close(pcm);

    return byte_count;
}

static int write_file(const void *frames, size_t size)
{
    FILE *output_file = fopen("audio.raw", "wb");
    if (output_file == NULL) {
        perror("failed to open 'audio.raw' for writing");
        return EXIT_FAILURE;
    }
    fwrite(frames, 1, size, output_file);
    fclose(output_file);
    return 0;
}

int main(void)
{
    fprintf(stdout, "TinyALSA test_package\n");
    void *frames = NULL;
    size_t size = 0;

    size = read_frames(&frames);
    if (size == 0) {
        return EXIT_FAILURE;
    }

    if (write_file(frames, size) < 0) {
        free(frames);
        return EXIT_FAILURE;
    }

    free(frames);

    return EXIT_SUCCESS;
}
