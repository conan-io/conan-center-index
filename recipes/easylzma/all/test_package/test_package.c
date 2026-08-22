#include "easylzma/compress.h"

#include <stdio.h>

int main() {
    printf("EasyLZMA test package \n");

    int rc;
    int inLen = 10;
    elzma_file_format format = ELZMA_lzma;
    elzma_compress_handle hand;

    /* allocate compression handle */
    hand = elzma_compress_alloc();
    if (hand == NULL) {
        printf("Allocation failed \n");
        return 0;
    }

    rc = elzma_compress_config(hand, ELZMA_LC_DEFAULT,
                               ELZMA_LP_DEFAULT, ELZMA_PB_DEFAULT,
                               5, (1 << 20) /* 1mb */,
                               format, inLen);

    if (rc != ELZMA_E_OK) {
        printf("Config failed with error code: %d \n", rc);
    } else {
        printf("Config OK \n");
    }

    elzma_compress_free(&hand);
    return 0;
}
