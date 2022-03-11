#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>
#include <openssl/ssl.h>
#if defined(WITH_ZLIB)
#include <zlib.h>
#endif

#if defined(_MSC_VER) && _MSC_VER < 1900
#define snprintf _snprintf
#endif

#if OPENSSL_VERSION_NUMBER > 0x10101000L
#define OPENSSL_1_1_1_OR_LATER
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
	unsigned char md5_digest[MD5_DIGEST_LENGTH],
		sha1_digest[SHA_DIGEST_LENGTH],
		sha256_digest[SHA256_DIGEST_LENGTH],
		sha512_digest[SHA512_DIGEST_LENGTH],
		sha3_256_digest[SHA256_DIGEST_LENGTH],
		sha3_512_digest[SHA512_DIGEST_LENGTH];
	char md5_string[MD5_DIGEST_LENGTH*2+1] = {0},
		sha1_string[SHA_DIGEST_LENGTH*2+1] = {0},
		sha256_string[SHA256_DIGEST_LENGTH*2+1] = {0},
		sha512_string[SHA512_DIGEST_LENGTH*2+1] = {0},
		sha3_256_string[SHA256_DIGEST_LENGTH*2+1] = {0},
		sha3_512_string[SHA512_DIGEST_LENGTH*2+1] = {0};
	char string[] = "happy";

#if OPENSSL_VERSION_NUMBER < 0x10100000L
	SSL_library_init();
#else
	OPENSSL_init_ssl(0, NULL);
#endif

	MD5((unsigned char*)&string, strlen(string), (unsigned char*)&md5_digest);
	SHA1((unsigned char*)&string, strlen(string), (unsigned char*)&sha1_digest);
	SHA256((unsigned char*)&string, strlen(string), (unsigned char*)&sha256_digest);
	SHA512((unsigned char*)&string, strlen(string), (unsigned char*)&sha512_digest);
#ifdef OPENSSL_1_1_1_OR_LATER
	SHA3_hash(EVP_sha3_256(), (unsigned char*)&string, strlen(string), (unsigned char*)&sha3_256_digest, &digest_len);
	SHA3_hash(EVP_sha3_512(), (unsigned char*)&string, strlen(string), (unsigned char*)&sha3_512_digest, &digest_len);
#endif
	int i;
	for(i = 0; i < MD5_DIGEST_LENGTH; i++)
		 snprintf(&md5_string[i*2], sizeof(md5_string)-i*2, "%02x", (unsigned int)md5_digest[i]);

	for(i = 0; i < SHA_DIGEST_LENGTH; i++)
		 snprintf(&sha1_string[i*2], sizeof(sha1_string)-i*2, "%02x", (unsigned int)sha1_digest[i]);

	for(i = 0; i < SHA256_DIGEST_LENGTH; i++) {
		 snprintf(&sha256_string[i*2], sizeof(sha256_string)-i*2, "%02x", (unsigned int)sha256_digest[i]);
		 snprintf(&sha3_256_string[i*2], sizeof(sha3_256_string)-i*2, "%02x", (unsigned int)sha3_256_digest[i]);
	}

	for(i = 0; i < SHA512_DIGEST_LENGTH; i++) {
		 snprintf(&sha512_string[i*2], sizeof(sha512_string)-i*2, "%02x", (unsigned int)sha512_digest[i]);
		 snprintf(&sha3_512_string[i*2], sizeof(sha3_512_string)-i*2, "%02x", (unsigned int)sha3_512_digest[i]);
	}

	printf("md5 digest: %s\n", md5_string);
	printf("sha1 digest: %s\n", sha1_string);
	printf("sha256 digest: %s\n", sha256_string);
	printf("sha512 digest: %s\n", sha512_string);
#ifdef OPENSSL_1_1_1_OR_LATER
	printf("sha3 256 digest: %s\n", sha3_256_string);
	printf("sha3 512 digest: %s\n", sha3_512_string);
#endif
#if OPENSSL_VERSION_NUMBER < 0x10100000L
	printf("SSL library version: %s\n", SSLeay_version(SSLEAY_VERSION));
#else
	printf("SSL library version: %s\n", OpenSSL_version(OPENSSL_VERSION));
#endif
#if defined(WITH_ZLIB)
	printf("ZLIB version: %s\n", ZLIB_VERSION);
#endif

	return 0;
}
