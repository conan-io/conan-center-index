#include "x265.h"

#include <stdlib.h>

#ifdef WITH_LIB
# ifdef _WIN32
#  define TEST_IMPORT __declspec(dllimport)
# else
#  define TEST_IMPORT
# endif

TEST_IMPORT const char *test_library_version(void);
TEST_IMPORT void test_library_something(void);
#endif

int main()
{
    x265_param * param = x265_param_alloc();
    x265_param_default(param);
    param->sourceWidth = 640;
    param->sourceHeight = 480;
    param->fpsNum = 25;
    param->fpsDenom = 1;
    x265_encoder * encoder = x265_encoder_open(param);
    x265_encoder_close(encoder);
    x265_param_free(param);
#ifdef WITH_LIB
    test_library_version();
    test_library_something();
#endif
    return EXIT_SUCCESS;
}
