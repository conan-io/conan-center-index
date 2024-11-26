#include <libpopcnt.h>
#include <stdio.h>
#include <inttypes.h>

int main() {
  const char data = 0xff;
  uint64_t bits = popcnt(&data, sizeof(char));
  printf("popcnt(0xff) = %" PRIu64 " (expected 8) - Test package successful \n", bits);
  return 0;
}
