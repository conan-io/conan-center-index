#include "xxhash.h"

#include <iostream>
#include <stdlib.h>


int main()
{
    size_t const bufferSize = 10;
    void* const buffer = malloc(bufferSize);
    XXH64_hash_t hash = XXH64(buffer, bufferSize, 0);
    std::cout << hash << std::endl;
    free(buffer);
    return 0;
}
