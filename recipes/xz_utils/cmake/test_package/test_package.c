#include <stdio.h>
#include <stdlib.h>
#include <lzma.h>

int main() {
    printf("LZMA version %s\n", lzma_version_string());
    return EXIT_SUCCESS;
}
