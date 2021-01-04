
#ifdef _WIN32
#  define _CRT_SECURE_NO_WARNINGS 1
#endif

#include "mdns.h"

#include <stdio.h>
#include <errno.h>

#ifdef _WIN32
#  include <iphlpapi.h>
#  define sleep(x) Sleep(x * 1000)
#else
#  include <netdb.h>
#endif

int
main(int argc, const char* const* argv) {
#ifdef _WIN32
	WORD versionWanted = MAKEWORD(1, 1);
	WSADATA wsaData;
	if (WSAStartup(versionWanted, &wsaData)) {
		printf("Failed to initialize WinSock\n");
		return -1;
	}
#endif

	int port = 0;
	int sock = mdns_socket_open_ipv4(port);
	if (sock < 0) {
		printf("Failed to open socket: %s\n", strerror(errno));
		return -1;
	}

	printf("socket cleanup\n");
	mdns_socket_close(sock);
#ifdef _WIN32
	WSACleanup();
#endif

	return 0;
}
