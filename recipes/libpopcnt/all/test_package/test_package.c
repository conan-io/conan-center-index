#include "libpopcnt.h"

#include <stdlib.h>
#include <stdint.h>
#include <string.h>

int main() {
  int i = 0;
  size_t size = 42;
  uint8_t* data = (uint8_t*) malloc(size);

  memset(data, 0xff, size);

  uint64_t bits = popcnt(&data[i], size - i);

  return 0;
}
