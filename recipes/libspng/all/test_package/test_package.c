#include <stdio.h>
#include <string.h>

#include "spng.h"

int main(void) {
  fprintf(stderr, " Compiled with libspng %s.\n", spng_version_string());

  return 0;
}
