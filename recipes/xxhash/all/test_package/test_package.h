#include "xxhash.h"

#include <stdio.h>
#include <stdlib.h>

static void compute_hash()
{
    size_t const bufferSize = 10;
    void* const buffer = malloc(bufferSize);
    XXH64_hash_t hash = XXH64(buffer, bufferSize, 0);
    printf("%llu", hash);
    free(buffer);
}

void compute_hash_in_another_tu();
