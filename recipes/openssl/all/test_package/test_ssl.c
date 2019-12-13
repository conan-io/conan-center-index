#include <openssl/opensslconf.h>
#include <openssl/ssl.h>

#include <stdio.h>

int main() {
    unsigned long ssl_err = 0;
    SSL_library_init();
    SSL_load_error_strings();
    OPENSSL_config(NULL);
    const SSL_METHOD* method = SSLv23_method();
    ssl_err = ERR_get_error();

    if(method == NULL) {
        printf(stderr, "SSLv23_method failed\n");
        return 1;
    }
    SSL_CTX *ctx = SSL_CTX_new(method);
    if(ctx == NULL) {
        printf(stderr, "SSL_CTX_new failed\n");
        return 1;
    }
    SSL_CTX_free(ctx);
    return 0;
}
