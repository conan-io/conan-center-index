#include <stdio.h>
#include <string.h>

#include "iya_oidc.h"

int main(void) {
  const char *scopes = iya_oidc_default_scopes();
  if (scopes == NULL || scopes[0] == '\0') {
    fprintf(stderr, "no default scopes\n");
    return 1;
  }
  printf("iya-oidc-caep-risc: %s\n", scopes);
  return 0;
}
