#include "x265.h"

#include <stdlib.h>

#ifdef _WIN32
# define TEST_EXPORT __declspec(dllexport)
#else
# define TEST_EXPORT __attribute__ ((visibility("default")))
#endif

TEST_EXPORT const char *test_library_version(void) {
    return x265_version_str;
}

TEST_EXPORT void test_library_something(void) {
    x265_param * param = x265_param_alloc();
    x265_param_default(param);
    param->sourceWidth = 640;
    param->sourceHeight = 480;
    param->fpsNum = 25;
    param->fpsDenom = 1;
    x265_encoder * encoder = x265_encoder_open(param);
    x265_encoder_close(encoder);
    x265_param_free(param);
}
