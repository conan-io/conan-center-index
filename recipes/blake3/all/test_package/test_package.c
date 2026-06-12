#include <blake3.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    blake3_hasher hasher;
    blake3_hasher_init(&hasher);

    const char *input = "Hello, BLAKE3!";
    blake3_hasher_update(&hasher, input, strlen(input));

    uint8_t output[BLAKE3_OUT_LEN];
    blake3_hasher_finalize(&hasher, output, BLAKE3_OUT_LEN);

    printf("BLAKE3 hash: ");
    for (size_t i = 0; i < BLAKE3_OUT_LEN; i++) {
        printf("%02x", output[i]);
    }
    printf("\n");

    return 0;
}
