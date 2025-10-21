#include <stdio.h>
#include <stdlib.h>

#ifdef ZLIB_COMPAT
#  include "zlib.h"
#  define GET_ZLIB_VERSION zlibVersion
#else
#  include "zlib-ng.h"
#  define GET_ZLIB_VERSION zlibng_version
#endif

int main(void) {
    printf("ZLIB NG VERSION: %s\n", GET_ZLIB_VERSION());
    return EXIT_SUCCESS;
}
