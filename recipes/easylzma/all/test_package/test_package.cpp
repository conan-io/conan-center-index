#include <iostream>
#include <assert.h>

#include "easylzma/compress.h"

int main(){

    std::cout << "EasyLZMA test package" << std::endl;

    int rc;
    int inLen = 10;
    elzma_file_format format = ELZMA_lzma;
    elzma_compress_handle hand;

    /* allocate compression handle */
    hand = elzma_compress_alloc();
    assert(hand != NULL);

    rc = elzma_compress_config(hand, ELZMA_LC_DEFAULT,
                               ELZMA_LP_DEFAULT, ELZMA_PB_DEFAULT,
                               5, (1 << 20) /* 1mb */,
                               format, inLen);

    if (rc != ELZMA_E_OK) {
        std::cout << "Config failed with error code: " << rc << std::endl;
    } else {
        std::cout << "Config OK" << std::endl;
    }

    elzma_compress_free(&hand);
    return 0;
}