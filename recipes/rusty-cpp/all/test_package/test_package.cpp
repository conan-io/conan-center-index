#include <iostream>
#include <rusty/primitive.h>

int main(void) {
  size_t x = 233;
  std::cout << "The next power of two of " << x << " is "
            << rusty::next_power_of_two(x) << std::endl;

  return EXIT_SUCCESS;
}
