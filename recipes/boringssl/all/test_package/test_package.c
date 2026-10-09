#include <stdlib.h>
#include <stdio.h>
#include <openssl/ssl.h>

int main() {
    OPENSSL_init_ssl(0, NULL);
    printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));
    return EXIT_SUCCESS;
}