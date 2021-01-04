#include <cstdlib>
#include <cstring>
#include <iostream>
#include <fdk-aac/aacenc_lib.h>
#include <fdk-aac/aacdecoder_lib.h>

int main()
{
    LIB_INFO info[FDK_MODULE_LAST];
    memset(&info, 0, sizeof(info));
    int ret = aacDecoder_GetLibInfo(info);
    if (0 != ret) {
        std::cerr << "aacDecoder_GetLibInfo failed with " << ret << std::endl;
        return EXIT_FAILURE;
    }
    ret = aacEncGetLibInfo(info);
    if (0 != ret) {
        std::cerr << "aacEncGetLibInfo failed with " << ret << std::endl;
        return EXIT_FAILURE;
    }

    for (int i = 0; i < FDK_MODULE_LAST; ++i) {
        if (FDK_AACDEC == info[i].module_id || FDK_AACENC == info[i].module_id) {
            std::cout << info[i].title << std::endl;
            std::cout << info[i].build_date << std::endl;
            std::cout << info[i].build_time << std::endl;
            std::cout << info[i].versionStr << std::endl;
        }
    }

    return EXIT_SUCCESS;
}
