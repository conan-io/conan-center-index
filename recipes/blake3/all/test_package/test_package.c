#include <blake3.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    printf("BLAKE3 Version: %s\n", blake3_version());
    return EXIT_SUCCESS;
}
