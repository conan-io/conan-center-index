#include <cstdlib>
#include <iostream>

#include "stringzilla.h"

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
