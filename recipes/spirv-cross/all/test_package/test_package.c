#include <spirv_cross/spirv_cross_c.h>

#include <stdio.h>

int main() {
  unsigned major, minor, patch;
  spvc_get_version(&major, &minor, &patch);
  printf("SPIRV-Cross: C API version %u.%u.%u\n", major, minor, patch);
  return 0;
}
