#include "libpsl.h"

#include <stdio.h>

int main()
{
    printf("libpsl version: %s\n", psl_get_version());
    return 0;
}
