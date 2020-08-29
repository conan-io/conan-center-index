#include "mbedtls/version.h"

#include <cstdlib>
#include <cstdio>

int main()
{
    char mbedtls_version[18];
    mbedtls_version_get_string_full(mbedtls_version);
    printf("version: %s\n", mbedtls_version);

    return EXIT_SUCCESS;
}
