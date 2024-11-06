#include "libpopcnt.h"

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <string.h>

/*
 * Count 1 bits from &data[i] till &data[size].
 * @data: An array for testing
 * @size: size of data
 * @i: Array start index
 */
void test(uint8_t* data, size_t size, size_t i) {
  uint64_t bits = popcnt(&data[i], size - i);
  uint64_t bits_verify = 0;

  for (; i < size; i++)
    bits_verify += popcnt64_bitwise(data[i]);

  if (bits != bits_verify) {
    printf("\nlibpopcnt test failed!\n");
    free(data);
    exit(1);
  }
}

int main() {
  size_t i;
  size_t size = 70000;

  uint8_t* data = (uint8_t*) malloc(size);

  if (!data) {
    printf("Failed to allocate memory!\n");
    exit(1);
  }

  /* init array with only 1 bits */
  memset(data, 0xff, size);
  test(data, size, 0);

  srand((unsigned) time(0));

  /* generate array with random data */
  for (i = 0; i < size; i++)
    data[i] = (uint8_t) rand();

  for (i = 0; i < size; i++)
    test(data, size, i);

  free(data);

  printf("\rStatus: 100%%\n");
  printf("libpopcnt tested successfully!\n");

  return 0;
}
