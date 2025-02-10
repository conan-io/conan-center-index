#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "libwebsockets.h"

int main() {
	const char* lws_version = lws_get_library_version();
	printf("libwebsocket version: %s\n", lws_version);
	return 0;
}
