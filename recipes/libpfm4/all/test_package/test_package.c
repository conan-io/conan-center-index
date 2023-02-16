#include <stdlib.h>
#include <stdio.h>
#include <perfmon/err.h>
#include <perfmon/pfmlib.h>


int main(void) {
    int version = 0;

    pfm_initialize();
    version = pfm_get_version();
    printf("PFM VERSION: %d\n", version);
    pfm_terminate();

    return EXIT_SUCCESS;
}
