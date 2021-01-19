#include <hiredis/hiredis.h>

#include <stdlib.h>
#include <stdio.h>

#ifdef _MSC_VER
#include <winsock2.h>
#endif

int main() {
  printf("hiredis version: %i.%i.%i\n", HIREDIS_MAJOR, HIREDIS_MINOR, HIREDIS_PATCH);

  const char *hostname = "127.0.0.1";
  int port = 6379;
  struct timeval timeout = {2, 0};

  redisContext *c = redisConnectWithTimeout(hostname, port, timeout);
  if (c == NULL) {
    printf("Error: Can't allocate redis context\n");
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
