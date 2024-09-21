#include <aes.h>

int main() {
    aes_encrypt_ctx ctx;
    char message[] = "test";
    char key[] = "0123456789ABCDEF";
    aes_encrypt(message, key, &ctx);

    return 0;
}
