#include <cstdlib>
#include <iostream>

#include "stringzilla.h"

int main(void) {
  // Initialize your haystack and needle
  sz_string_view_t haystack = {
    "Fastest string sort, search, split, "
    "and shuffle for long strings and multi-gigabyte files in Python and C, "
    "leveraging SIMD with Arm Neon and x86 AVX2 & AVX-512 intrinsics.",
    171};
  sz_string_view_t needle = {"SIMD", 4};

  // Perform string-level operations
  sz_size_t character_count = sz_count_char(haystack.start, haystack.length, "a");
  sz_string_start_t substring_position = sz_find_substring(
    haystack.start, haystack.length,
    needle.start, needle.length
  );

  // Hash strings
  sz_u32_t crc32 = sz_hash_crc32(haystack.start, haystack.length);

  return EXIT_SUCCESS;
}
