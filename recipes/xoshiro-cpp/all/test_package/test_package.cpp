#include <cassert>
#include <iostream>

#include "xoshiro-cpp/XoshiroCpp.hpp"

template <class N> static void assert_and_print(N expected, N got) {
  std::cout << expected << " == " << got << '\n';
  assert(expected == got);
}

int main() {
  std::cout << "# Initialize with a default 64-bit seed\n";
  XoshiroCpp::Xoshiro256PlusPlus rng;
  for (uint64_t expected : {10656210946825422025ULL, 3029598875750717312ULL,
                            8253387787243700537ULL}) {
    assert_and_print(expected, rng());
  }
}
