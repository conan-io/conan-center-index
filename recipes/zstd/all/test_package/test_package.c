#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zstd.h>

int main() {
    const char* originalData = "Sample text";
    size_t compressedSize = ZSTD_compressBound(strlen(originalData) + 1);
    printf("%zu\n", compressedSize);

    return 0;
}
