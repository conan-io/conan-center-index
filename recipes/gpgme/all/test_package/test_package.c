#include "gpgme.h"

#include <stdio.h>

int main() {
  printf("version: %s\nversion number: 0x%08x\n", GPGME_VERSION, GPGME_VERSION_NUMBER);
  return 0;
}
