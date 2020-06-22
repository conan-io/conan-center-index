#include "libmdnsd/mdnsd.h"

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include "Windows.h"
#include <winsock2.h>
#include <ws2tcpip.h>
#define CLOSESOCKET(S) closesocket((SOCKET)S)
#define ssize_t int
#else
#include <unistd.h>
#define CLOSESOCKET(S) close(S)
#endif

static void socket_set_nonblocking(int sockfd) {
#ifdef _WIN32
  u_long iMode = 1;
  ioctlsocket(sockfd, FIONBIO, &iMode);
#else
  int opts = fcntl(sockfd, F_GETFL);
  fcntl(sockfd, F_SETFL, opts | O_NONBLOCK);
#endif
}

int msock(void) {
  int s, flag = 1, ittl = 255;
  struct sockaddr_in in;
  struct ip_mreq mc;
  unsigned char ttl = 255; // send to any reachable net, not only the subnet

  memset(&in, 0, sizeof(in));
  in.sin_family = AF_INET;
  in.sin_port = htons(5353);
  in.sin_addr.s_addr = 0;

  if ((s = (int)socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    return 0;

#ifdef SO_REUSEPORT
  setsockopt(s, SOL_SOCKET, SO_REUSEPORT, (char *)&flag, sizeof(flag));
#endif
  setsockopt(s, SOL_SOCKET, SO_REUSEADDR, (char *)&flag, sizeof(flag));
  if (bind(s, (struct sockaddr *)&in, sizeof(in))) {
    CLOSESOCKET(s);
    return 0;
  }

  mc.imr_multiaddr.s_addr = inet_addr("224.0.0.251");
  mc.imr_interface.s_addr = htonl(INADDR_ANY);
  setsockopt(s, IPPROTO_IP, IP_ADD_MEMBERSHIP, (void *)&mc, sizeof(mc));
  setsockopt(s, IPPROTO_IP, IP_MULTICAST_TTL, (void *)&ttl, sizeof(ttl));
  setsockopt(s, IPPROTO_IP, IP_MULTICAST_TTL, (void *)&ittl, sizeof(ittl));

  socket_set_nonblocking(s);

  return s;
}

int main() {

  mdns_daemon_t *daemon = mdnsd_new(QCLASS_IN, 1000);
  if (msock() == 0) {
    printf("can't create socket: %s\n", strerror(errno));
    return 1;
  }

  sleep(1);
  mdnsd_shutdown(daemon);
  if (write(0, "\0", 1) == -1) {
    printf("Could not write zero byte to socket\n");
  }
  mdnsd_free(daemon);

  return 0;
}
