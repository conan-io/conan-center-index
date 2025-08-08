#include <stdio.h>
#include <stdlib.h>

#include <zlib.h>

int zlib_test_vsnprintf(void) {
#ifdef WITH_TEST_VSNPRINTF
    // 25th bit indicates vsnprinft support
    // 26th bit indicates whether vnsprinft returned void at compile time (i.e. doesn't work correctly)
    // from the zlib.h header:
    // > 25: 0 = *nprintf, 1 = *printf -- 1 means gzprintf() not secure!
    // > 26: 0 = returns value, 1 = void -- 1 means inferred string length returned
    uLong flags = zlibCompileFlags();

    uLong flag_vsnprintf_support = 1L << 25;
    uLong flag_vsnprintf_void_ret = 1L << 26;

    if ((flags & flag_vsnprintf_support) == flag_vsnprintf_support || (flags & flag_vsnprintf_void_ret) == flag_vsnprintf_void_ret) {
        printf("ZLIB is not compiled with vnsprinft support\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
#else
    return EXIT_SUCCESS;
#endif
}

int main(void) {

    printf("ZLIB VERSION: %s\n", zlibVersion());

    return zlib_test_vsnprintf();
}
