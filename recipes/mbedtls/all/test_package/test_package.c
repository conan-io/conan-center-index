#include "mbedtls/version.h"
#include "mbedtls/platform.h"

#include <stdio.h>

int main()
{
    char buf[10];
    mbedtls_snprintf(buf, sizeof(buf), "%d", 100);

    char mbedtls_version[18];
    mbedtls_version_get_string_full(mbedtls_version);
    printf("version: %s\n", mbedtls_version);

    return 0;
}
