#include "xxhash.h"
#include <iostream>


int main()
{
    size_t const bufferSize = 10;
    void* const buffer = malloc(bufferSize);
    XXH64_hash_t hash = XXH64(buffer, 8, 1);
    std::cout << hash << std::endl;
    free(buffer);
    return 0;
}
