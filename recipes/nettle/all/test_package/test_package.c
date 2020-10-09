#include <nettle/sha1.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void display_hex(size_t length, uint8_t *data) {
    size_t i;

    for (i = 0; i<length; i++) {
        printf("%02x ", data[i]);
    }

    printf("\n");
}

#define CLEARTEXT "Conan-Center-Index"

int main(void) {
    struct sha1_ctx ctx;
    uint8_t digest[SHA1_DIGEST_SIZE];
    uint8_t *data = CLEARTEXT;

    sha1_init(&ctx);
    sha1_update(&ctx, strlen(data), data);
    sha1_digest(&ctx, SHA1_DIGEST_SIZE, digest);

    display_hex(SHA1_DIGEST_SIZE, digest);
    return EXIT_SUCCESS;
}
