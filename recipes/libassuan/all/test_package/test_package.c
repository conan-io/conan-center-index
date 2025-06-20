#include "assuan.h"

#include <stdio.h>

int main() {
  printf("version: %s\nversion number: 0x%08x\n", ASSUAN_VERSION, ASSUAN_VERSION_NUMBER);
  return 0;
}
