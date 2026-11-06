#include <noqtis.h>

#include <stdio.h>

int main(void) {
  uint8_t d[32];
  if (nqhash(NQS256, (const uint8_t *)"abc", 3, d, sizeof d) != NQOK)
    return 1;
  printf("noqtis %s sha256(abc) %02x%02x...\n", nqver(), d[0], d[1]);
  return !(d[0] == 0xba && d[1] == 0x78);
}
