#include <stdio.h>
#include <string.h>

#include "iya_wsfed.h"

int main(void) {
  const char *status = iya_wsfed_status_success();
  if (status == NULL || status[0] == '\0') {
    fprintf(stderr, "no success status\n");
    return 1;
  }
  printf("iya-wsfed-caep: %s\n", status);
  return 0;
}
