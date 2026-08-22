#include <fdk-aac/aacenc_lib.h>
#include <fdk-aac/aacdecoder_lib.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int main()
{
    LIB_INFO info[FDK_MODULE_LAST];
    memset(&info, 0, sizeof(info));
    int ret = aacDecoder_GetLibInfo(info);
    if (0 != ret) {
        fprintf(stderr, "aacDecoder_GetLibInfo failed with %u\n", ret);
        return EXIT_FAILURE;
    }
    ret = aacEncGetLibInfo(info);
    if (0 != ret) {
        fprintf(stderr, "aacEncGetLibInfo failed with %u\n", ret);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < FDK_MODULE_LAST; ++i) {
        if (FDK_AACDEC == info[i].module_id || FDK_AACENC == info[i].module_id) {
            printf("title:      %s\n", info[i].title);
            printf("build date: %s\n", info[i].build_date);
            printf("build time: %s\n", info[i].build_time);
            printf("version:    %s\n", info[i].versionStr);
            printf("========================================\n");
        }
    }

    return EXIT_SUCCESS;
}
