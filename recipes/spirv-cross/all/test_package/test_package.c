#include <spirv_cross_c.h>

#include <stdio.h>

int main() {
  spvc_context context;
  spvc_context_create(&context);
  spvc_context_destroy(context);

  unsigned major, minor, patch;
  spvc_get_version(&major, &minor, &patch);
  printf("SPIRV-Cross: C API version %u.%u.%u\n", major, minor, patch);

  return 0;
}
