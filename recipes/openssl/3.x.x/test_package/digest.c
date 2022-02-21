#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>
#include <openssl/ssl.h>
#if defined(WITH_ZLIB)
#include <zlib.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_MSC_VER) && _MSC_VER < 1900
#define snprintf _snprintf
#endif

void SHA3_hash(const EVP_MD *type, const unsigned char *message, size_t message_len, unsigned char *digest, unsigned int *digest_len) {
    EVP_MD_CTX *mdctx;

    if((mdctx = EVP_MD_CTX_create()) == NULL)
        printf("EVP_MD_CTX_create error!\n");

    if(EVP_DigestInit_ex(mdctx, type, NULL) != 1)
        printf("EVP_DigestInit_ex error!\n");

    if(EVP_DigestUpdate(mdctx, message, message_len) != 1)
        printf("EVP_DigestUpdate error!\n");

    if(EVP_DigestFinal_ex(mdctx, digest, digest_len) != 1)
        printf("EVP_DigestFinal_ex error!\n");

    EVP_MD_CTX_destroy(mdctx);
}

int main()
{
    unsigned int digest_len;
    unsigned char sha256_digest[SHA256_DIGEST_LENGTH],
        sha512_digest[SHA512_DIGEST_LENGTH],
        sha3_256_digest[SHA256_DIGEST_LENGTH],
        sha3_512_digest[SHA512_DIGEST_LENGTH];
    char sha256_string[SHA256_DIGEST_LENGTH*2+1] = {0},
        sha512_string[SHA512_DIGEST_LENGTH*2+1] = {0},
        sha3_256_string[SHA256_DIGEST_LENGTH*2+1] = {0},
        sha3_512_string[SHA512_DIGEST_LENGTH*2+1] = {0};
    char string[] = "happy";

    SHA256((unsigned char*)&string, strlen(string), (unsigned char*)&sha256_digest);
    SHA512((unsigned char*)&string, strlen(string), (unsigned char*)&sha512_digest);
    SHA3_hash(EVP_sha3_256(), (unsigned char*)&string, strlen(string), (unsigned char*)&sha3_256_digest, &digest_len);
    SHA3_hash(EVP_sha3_512(), (unsigned char*)&string, strlen(string), (unsigned char*)&sha3_512_digest, &digest_len);

    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        snprintf(&sha256_string[i*2], sizeof(sha256_string)-i*2, "%02x", (unsigned int)sha256_digest[i]);
        snprintf(&sha3_256_string[i*2], sizeof(sha3_256_string)-i*2, "%02x", (unsigned int)sha3_256_digest[i]);
    }

    for(int i = 0; i < SHA512_DIGEST_LENGTH; i++) {
        snprintf(&sha512_string[i*2], sizeof(sha512_string)-i*2, "%02x", (unsigned int)sha512_digest[i]);
        snprintf(&sha3_512_string[i*2], sizeof(sha3_512_string)-i*2, "%02x", (unsigned int)sha3_512_digest[i]);
    }

    printf("sha256 digest: %s\n", sha256_string);
    printf("sha512 digest: %s\n", sha512_string);
    printf("sha3 256 digest: %s\n", sha3_256_string);
    printf("sha3 512 digest: %s\n", sha3_512_string);
    printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));
#if defined(WITH_ZLIB)
    printf("ZLIB version: %s\n", ZLIB_VERSION);
#endif

    return 0;
}
