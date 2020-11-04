#include <libdivide.h>

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int main() {
  struct libdivide_s64_t fast_d = libdivide_s64_gen(30);
  int64_t a = 60;
  printf("%" PRId64 "\n", libdivide_s64_do(a, &fast_d));
  return 0;
}
