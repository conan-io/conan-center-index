#include <stdio.h>
#include <openssl/ssl.h>

void digest();
int digest_legacy();

int main()
{
	int legacy_result = 0;
	OPENSSL_init_ssl(0, NULL);
	printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));
	
	digest();

#if defined(TEST_OPENSSL_LEGACY)
	legacy_result = digest_legacy();
	if (legacy_result != 0) {
		printf("Error testing the digest_legacy() function\n");
		return 1;
	}
#endif

	return 0;
}
