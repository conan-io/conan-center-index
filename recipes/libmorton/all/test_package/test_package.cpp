#include <libmorton/morton.h>

#include <iostream>

int main() {
  std::cout << libmorton::morton3D_64_encode(1, 2, 3) << std::endl;
  return 0;
}
