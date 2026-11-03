#include <stdio.h>
#include <string.h>

#include "iya_gnap.h"

int main(void) {
  iya_gnap_error err;
  char *digest = NULL;
  memset(&err, 0, sizeof err);
  if (iya_gnap_content_digest("hello", &digest, &err) != 0 || digest == NULL) {
    fprintf(stderr, "content digest failed\n");
    return 1;
  }
  printf("iya-gnap-caep-risc: %s\n", digest);
  iya_gnap_free(digest);
  return 0;
}
