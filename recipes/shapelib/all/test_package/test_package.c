#include "shapefil.h"

#include <stdlib.h>

int main() {
  char out_file_name[] = "test";
  SHPHandle hSHP = SHPCreate(out_file_name, SHPT_POLYGONZ);

  if (hSHP == NULL) {
    printf("Unable to create:%s\n", out_file_name);
    exit(EXIT_FAILURE);
  }

  SHPClose(hSHP);

  exit(EXIT_SUCCESS);
}
