#include <gta/gta.h>

#include <stdio.h>
#include <stdlib.h>

int main() {
  gta_header_t *header;
  gta_result_t r = gta_create_header(&header);
  if (r != GTA_OK) {
    fprintf(stderr, "failed to create header");
    exit(1);
  }

  return 0;
}
