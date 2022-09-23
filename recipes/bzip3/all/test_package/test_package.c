#include <stdio.h>
#include <string.h>

#include "libbz3.h"

int main() {
  const unsigned int block_size = 8 * 1024 * 1024;
  struct bz3_state * state = bz3_new(block_size);

  bz3_free(state);

  return 0;
}
