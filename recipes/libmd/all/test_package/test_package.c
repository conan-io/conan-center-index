#include <md5.h>
#include <string.h>

int main() {
    const char data[] = "12345";
    uint8_t hash[MD5_DIGEST_LENGTH];
    MD5_CTX md5_ctx;
    MD5Init(&md5_ctx);
    MD5Update(&md5_ctx, (const uint8_t *)data, strlen(data));
    MD5Final(hash, &md5_ctx);
    return 0;
}
