#include <openssl/ssl.h>
#include <string.h>
#include <stdio.h>

int main(int argc, char* argv[])
{
	SSL_library_init();
	SSL_CTX* ctx = SSL_CTX_new(SSLv23_client_method());
	if (!ctx)
		return -1;
	return 0;
}
