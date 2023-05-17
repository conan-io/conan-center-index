#include <stdio.h>
#include <stdlib.h>

#include "jxl/decode.h"
#include "jxl/thread_parallel_runner.h"

static int ReadFile(const char filename[], uint8_t *data[], size_t *size)
{
    FILE *fp = fopen(filename, "rb");
    if (!fp)
        return 0;

    if (fseek(fp, 0, SEEK_END) != 0) {
        fclose(fp);
        return 0;
    }

    *size = ftell(fp);
    if (fseek(fp, 0, SEEK_SET) != 0) {
        fclose(fp);
        return 0;
    }

    *data = malloc(*size);
    if (!*data) {
        fclose(fp);
        return 0;
    }

    if (fread(*data, sizeof(uint8_t), *size, fp) != *size) {
        free(*data);
        fclose(fp);
        return 0;
    }

    if (fclose(fp) != 0) {
        free(*data);
        return 0;
    }

    return 1;
}

int main(int argc, char *argv[])
{
    int ret = EXIT_FAILURE;
    
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return ret;
    }

    uint8_t *data;
    size_t size;
    if (!ReadFile(argv[1], &data, &size))
        return ret;

    JxlDecoder *dec = NULL;
    void *runner = NULL;

    dec = JxlDecoderCreate(NULL);
    if (JxlDecoderSubscribeEvents(dec, JXL_DEC_BASIC_INFO) != JXL_DEC_SUCCESS)
        goto Exit;

    runner = JxlThreadParallelRunnerCreate(
        NULL, JxlThreadParallelRunnerDefaultNumWorkerThreads());
    if (JxlDecoderSetParallelRunner(dec, JxlThreadParallelRunner, runner)
            != JXL_DEC_SUCCESS)
        goto Exit;

    if (JxlDecoderSetInput(dec, data, size) != JXL_DEC_SUCCESS)
        goto Exit;

    if (JxlDecoderProcessInput(dec) != JXL_DEC_BASIC_INFO)
        goto Exit;

    JxlBasicInfo info;
    if (JxlDecoderGetBasicInfo(dec, &info) != JXL_DEC_SUCCESS)
        goto Exit;

    printf("Image size: %d x %d pixels\n", info.xsize, info.ysize);

    ret = EXIT_SUCCESS;

Exit:
    free(data);
    JxlThreadParallelRunnerDestroy(runner);
    JxlDecoderDestroy(dec);
    return ret;
}
