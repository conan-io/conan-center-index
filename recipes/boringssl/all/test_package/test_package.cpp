#include <cstdlib>
#include <openssl/ssl.h>
#include <iostream>

int main() {
    OPENSSL_init_ssl(0, NULL);
    std::cout << "OpenSSL version: " << OpenSSL_version(OPENSSL_VERSION) << "\n";
    return EXIT_SUCCESS;
}