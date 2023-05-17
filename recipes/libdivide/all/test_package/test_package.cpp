#include <libdivide.h>

#include <cstdint>
#include <iostream>

int main() {
  libdivide::divider<int64_t> fast_d(30);
  int64_t a = 60;
  std::cout << a / fast_d << std::endl;
  return 0;
}
