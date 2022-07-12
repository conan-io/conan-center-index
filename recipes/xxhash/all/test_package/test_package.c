#include "xxhash.h"

#include <stdio.h>
#include <stdlib.h>


int main()
{
    size_t const bufferSize = 10;
    void* const buffer = malloc(bufferSize);
    XXH64_hash_t hash = XXH64(buffer, bufferSize, 0);
    printf("%llu", hash);
    free(buffer);
    return 0;
}
