#include <stdio.h>
#include <stdlib.h>

#include "hdf5.h"
#include "blosc2_filter.h"

int main(void) {
    char *version = NULL;
    char *date = NULL;

    if (register_blosc2(&version, &date) < 0) {
        fprintf(stderr, "register_blosc2 failed\n");
        return EXIT_FAILURE;
    }
    printf("Blosc2 filter registered (blosc2 %s, %s)\n", version, date);

    if (H5Zfilter_avail(FILTER_BLOSC2) <= 0) {
        fprintf(stderr, "Blosc2 filter not available after registration\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
