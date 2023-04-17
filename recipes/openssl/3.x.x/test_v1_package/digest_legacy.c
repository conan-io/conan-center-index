#include <openssl/evp.h>
#if OPENSSL_WITH_MD4
#include <openssl/md4.h> // MD4 needs legacy provider
#endif
#if OPENSSL_WITH_RIPEMD160
#include <openssl/ripemd.h> // RIPEMD160 needs legacy provider
#endif
#include <openssl/md5.h>
#include <openssl/provider.h>
#include <openssl/err.h>
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

int MDx_hash(const EVP_MD *type, const unsigned char *message, size_t message_len, unsigned char *digest, unsigned int *digest_len) {
    EVP_MD_CTX *mdctx;

    if((mdctx = EVP_MD_CTX_create()) == NULL)
    {
        printf("EVP_MD_CTX_create error!\n");
        return 1;
    }

    if(EVP_DigestInit_ex(mdctx, type, NULL) != 1)
    {
        printf("EVP_DigestInit_ex error!\n");
        return 1;
    }

    if(EVP_DigestUpdate(mdctx, message, message_len) != 1)
    {
        printf("EVP_DigestUpdate error!\n");
        return 1;
    }

    if(EVP_DigestFinal_ex(mdctx, digest, digest_len) != 1)
    {
        printf("EVP_DigestFinal_ex error!\n");
        return 1;
    }

    EVP_MD_CTX_destroy(mdctx);
    return 0;
}

int main()
{
    unsigned int digest_len;
    unsigned char md5_digest[MD5_DIGEST_LENGTH];
    unsigned char md5_digest2[MD5_DIGEST_LENGTH];
    char md5_string[MD5_DIGEST_LENGTH*2+1] = {0};
    char md5_string2[MD5_DIGEST_LENGTH*2+1] = {0};
    char string[] = "happy";

    MD5((unsigned char*)&string, strlen(string), (unsigned char*)&md5_digest);
    if (MDx_hash(EVP_md5(), (unsigned char*)&string, strlen(string), (unsigned char*)&md5_digest2, &digest_len))
        return 1;

    for(int i = 0; i < MD5_DIGEST_LENGTH; i++) {
        snprintf(&md5_string[i*2], sizeof(md5_string)-i*2, "%02x", (unsigned int)md5_digest[i]);
        snprintf(&md5_string2[i*2], sizeof(md5_string2)-i*2, "%02x", (unsigned int)md5_digest2[i]);
    }

    // MD4 needs the legacy provider
    OSSL_LIB_CTX* context = OSSL_LIB_CTX_new();
    // From https://wiki.openssl.org/index.php/OpenSSL_3.0
    /* Load Multiple providers into the default (nullptr) library context */
    OSSL_PROVIDER* legacy = OSSL_PROVIDER_load(context, "legacy");
    if (0 == legacy) {
        const char* error_string = ERR_error_string(ERR_get_error(), 0);
        fprintf(stderr, "Loading legacy provider failed with this error:\n");
        fprintf(stderr, "\t%s\n", error_string);
        return 1;
    }
    OSSL_LIB_CTX* oldcontex = OSSL_LIB_CTX_set0_default(context);
    printf("Legacy provider successfully loaded.\n");

#if OPENSSL_WITH_MD4
    unsigned char md4_digest[MD4_DIGEST_LENGTH];
    unsigned char md4_digest2[MD4_DIGEST_LENGTH];
    char md4_string[MD4_DIGEST_LENGTH*2+1] = {0};
    char md4_string2[MD4_DIGEST_LENGTH*2+1] = {0};

    MD4((unsigned char*)&string, strlen(string), (unsigned char*)&md4_digest);
    if (MDx_hash(EVP_md4(), (unsigned char*)&string, strlen(string), (unsigned char*)&md4_digest2, &digest_len)) {
        const char* error_string = ERR_error_string(ERR_get_error(), 0);
        fprintf(stderr, "MD4 calculation failed with this error:\n");
        fprintf(stderr, "\t%s\n", error_string);
        return 1;
    }

    for(int i = 0; i < MD4_DIGEST_LENGTH; i++) {
        snprintf(&md4_string[i*2], sizeof(md4_string)-i*2, "%02x", (unsigned int)md4_digest[i]);
        snprintf(&md4_string2[i*2], sizeof(md4_string2)-i*2, "%02x", (unsigned int)md4_digest2[i]);
    }
#endif

#if OPENSSL_WITH_RIPEMD160
    unsigned char ripemd160_digest[RIPEMD160_DIGEST_LENGTH];
    unsigned char ripemd160_digest2[RIPEMD160_DIGEST_LENGTH];
    char ripemd160_string[RIPEMD160_DIGEST_LENGTH*2+1] = {0};
    char ripemd160_string2[RIPEMD160_DIGEST_LENGTH*2+1] = {0};

    RIPEMD160((unsigned char*)&string, strlen(string), (unsigned char*)&ripemd160_digest);
    if (MDx_hash(EVP_ripemd160(), (unsigned char*)&string, strlen(string), (unsigned char*)&ripemd160_digest2, &digest_len)) {
        const char* error_string = ERR_error_string(ERR_get_error(), 0);
        fprintf(stderr, "RIPEMD160 calculation failed with this error:\n");
        fprintf(stderr, "\t%s\n", error_string);
        return 1;
    }

    for(int i = 0; i < RIPEMD160_DIGEST_LENGTH; i++) {
        snprintf(&ripemd160_string[i*2], sizeof(ripemd160_string)-i*2, "%02x", (unsigned int)ripemd160_digest[i]);
        snprintf(&ripemd160_string2[i*2], sizeof(ripemd160_string2)-i*2, "%02x", (unsigned int)ripemd160_digest2[i]);
    }
#endif

    OSSL_LIB_CTX_set0_default(oldcontex);
    OSSL_PROVIDER_unload(legacy);
    OSSL_LIB_CTX_free(context);

    printf("MD5 digest: %s\n", md5_string);
    printf("MD5 digest (variant 2): %s\n", md5_string2);
#if OPENSSL_WITH_MD4
    printf("MD4 digest: %s\n", md4_string);
    printf("MD4 digest (variant 2): %s\n", md4_string2);
#endif
#if OPENSSL_WITH_RIPEMD160
    printf("RIPEMD160 digest: %s\n", ripemd160_string);
    printf("RIPEMD160 digest (variant 2): %s\n", ripemd160_string2);
#endif
    printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));
#if defined(WITH_ZLIB)
    printf("ZLIB version: %s\n", ZLIB_VERSION);
#endif

    return 0;
}
