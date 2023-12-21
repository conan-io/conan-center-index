#include <cstdlib>
#include <iostream>
#include <lzf.h>

int main(void) {
  const char in_data[] = "AAAAAAAAAAAAAAAAAAAAA";
  const unsigned int buf_len = 100;
  char compressed_data[buf_len];
  char decompressed_data[buf_len];
  unsigned int compressed_len = lzf_compress(in_data, sizeof(in_data), compressed_data, buf_len);
  unsigned int decompressed_len = lzf_decompress(compressed_data, compressed_len, decompressed_data, buf_len);
  if (compressed_len >= 10 || decompressed_len != sizeof(in_data)) {
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
