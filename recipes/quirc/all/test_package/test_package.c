#include <quirc.h>

#include <stdio.h>
#include <stdlib.h>

int main () {
  struct quirc *qr;
  qr = quirc_new();
  if (!qr) {
    fprintf(stderr, "Failed to allocate memory");
    exit(1);
  }

  return 0;
}
