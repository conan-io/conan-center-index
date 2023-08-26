#include <aes.h>

int main() {
    aes_encrypt_ctx ctx;
    char message[] = "test";
    aes_encrypt(message, message, &ctx);

    return 0;
}
