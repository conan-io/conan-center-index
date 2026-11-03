#include <stdio.h>
#include <string.h>

#include "iya_saml.h"

int main(void) {
  const char *uri = iya_saml_event_uri("risk_level_change");
  if (uri == NULL || uri[0] == '\0') {
    fprintf(stderr, "no event URI\n");
    return 1;
  }
  printf("iya-saml2-sp: %s\n", uri);
  return 0;
}
