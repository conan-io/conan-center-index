#include <cstdlib>
#include <iostream>
#if STRINGZILLA_API >= 3
#include <cstdint>
#include <vector>
#include "stringzilla/stringzilla.hpp"
#else
#include "stringzilla.h"
#endif

#if STRINGZILLA_API >= 3

namespace sz = ashvardanian::stringzilla;

int main(void) {
  sz::string haystack = "some string";
  sz::string_view needle = sz::string_view(haystack).substr(0, 4);

  auto substring_position = haystack.find(needle); // Or `rfind`

  haystack.end() - haystack.begin() == haystack.size(); // Or `rbegin`, `rend`
  haystack.find_first_of(" \w\t") == 4; // Or `find_last_of`, `find_first_not_of`, `find_last_not_of`
  haystack.starts_with(needle) == true; // Or `ends_with`
  haystack.remove_prefix(needle.size()); // Why is this operation in-place?!
}

#elif STRINGZILLA_API == 2

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

#else

int main(void) {
  // Initialize your haystack and needle
  strzl_haystack_t haystack = {
    "Fastest string sort, search, split, "
    "and shuffle for long strings and multi-gigabyte files in Python and C, "
    "leveraging SIMD with Arm Neon and x86 AVX2 & AVX-512 intrinsics.",
    171};
  strzl_needle_t needle = {"SIMD", 4};

  // Count occurrences of a character like a boss 😎
  size_t count = strzl_naive_count_char(haystack, 'a');

  // Find a character like you're searching for treasure 🏴‍☠️
  size_t position = strzl_naive_find_char(haystack, 'a');

  // Find a substring like it's Waldo 🕵️‍♂️
  size_t substring_position = strzl_naive_find_substr(haystack, needle);

  return EXIT_SUCCESS;
}

#endif
