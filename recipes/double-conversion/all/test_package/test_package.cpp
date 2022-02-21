#include <iostream>
#include "double-conversion/diy-fp.h"
#include "double-conversion/utils.h"
#include "double-conversion/ieee.h"

#ifndef UINT64_2PART_C
#define UINT64_2PART_C(a, b) DOUBLE_CONVERSION_UINT64_2PART_C(a, b)
#endif

int main() {
  uint64_t ordered = UINT64_2PART_C(0x01234567, 89ABCDEF);
  std::cout << "A value: " << double_conversion::Double(ordered).value() << std::endl;
  return 0;
}
