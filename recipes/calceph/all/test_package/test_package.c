#include <calceph.h>

#include <stdio.h>

int main(void) {
  char calceph_version[CALCEPH_MAX_CONSTANTNAME];
  calceph_getversion_str(calceph_version);
  printf("CALCEPH version %s\n", calceph_version);
  return 0;
}
