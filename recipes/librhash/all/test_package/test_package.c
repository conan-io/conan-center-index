#include "rhash.h"

#include <stdio.h>
#include <string.h>

#define MSG "hello world"
#define SHA256_REF "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

int main() {
    rhash_library_init();
    unsigned char rhash_bin_buffer[128];
    char rhash_char_buffer[128];
    rhash_msg(RHASH_SHA256, MSG, strlen(MSG), rhash_bin_buffer);
    int nb = rhash_print_bytes(rhash_char_buffer, rhash_bin_buffer, rhash_get_hash_length(RHASH_SHA256), RHPR_HEX);
    rhash_char_buffer[rhash_get_hash_length(RHASH_SHA256)] = '\0';
    printf("calculated SHA256 hash= %s\n", rhash_char_buffer);

    printf("reference SHA256 hash=  %s\n", SHA256_REF);
    return strcmp(rhash_char_buffer, SHA256_REF);
}
