#include <stdio.h>
#include <stdlib.h>

#include <zlib.h>

int main(void) {

    printf("ZLIB VERSION: %s\n", zlibVersion());

    return EXIT_SUCCESS;
}
