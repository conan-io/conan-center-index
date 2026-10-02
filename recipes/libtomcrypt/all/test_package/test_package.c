#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <tomcrypt.h>

int main(void) {
    /* SHA-256("abc") */
    static const unsigned char expected[32] = {
        0xba, 0x78, 0x16, 0xbf, 0x8f, 0x01, 0xcf, 0xea, 0x41, 0x41, 0x40, 0xde, 0x5d, 0xae, 0x22, 0x23,
        0xb0, 0x03, 0x61, 0xa3, 0x96, 0x17, 0x7a, 0x9c, 0xb4, 0x10, 0xff, 0x61, 0xf2, 0x00, 0x15, 0xad};
    const char *msg = "abc";
    unsigned char digest[32];
    unsigned long digest_len = sizeof(digest);
    void *n = NULL;
    int err;

    /* ltm_desc is only declared when LTM_DESC is defined: the package has to export it to its consumers */
    ltc_mp = ltm_desc;

    if (register_hash(&sha256_desc) == -1) {
        fprintf(stderr, "register_hash failed\n");
        return EXIT_FAILURE;
    }
    err = hash_memory(find_hash("sha256"), (const unsigned char *)msg, strlen(msg), digest, &digest_len);
    if (err != CRYPT_OK) {
        fprintf(stderr, "hash_memory failed: %s\n", error_to_string(err));
        return EXIT_FAILURE;
    }
    if (digest_len != sizeof(expected) || memcmp(digest, expected, sizeof(expected)) != 0) {
        fprintf(stderr, "unexpected SHA-256 digest\n");
        return EXIT_FAILURE;
    }

    /* exercise the LibTomMath backend */
    if (ltc_mp.init(&n) != CRYPT_OK) {
        fprintf(stderr, "mp_init failed\n");
        return EXIT_FAILURE;
    }
    ltc_mp.set_int(n, 42);
    err = ltc_mp.compare_d(n, 42);
    ltc_mp.deinit(n);
    if (err != LTC_MP_EQ) {
        fprintf(stderr, "unexpected math result\n");
        return EXIT_FAILURE;
    }

    printf("%s: %s, math backend: %s\n", error_to_string(CRYPT_OK), "SHA-256 OK", ltc_mp.name);
    return EXIT_SUCCESS;
}
