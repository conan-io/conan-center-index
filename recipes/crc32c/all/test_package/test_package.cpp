#include <iostream>
#include "crc32c/crc32c.h"


int main() {
  const std::uint8_t buffer[] = {0, 0, 0, 0};
  std::uint32_t result;

  // Process a raw buffer.
  result = crc32c::Crc32c(buffer, 4);
  std::cout << result << '\n';

  // Process a std::string.
  std::string string;
  string.resize(4);
  result = crc32c::Crc32c(string);
  std::cout << result << '\n';

  return 0;
}
