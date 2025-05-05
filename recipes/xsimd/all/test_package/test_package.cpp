#include "xsimd/xsimd.hpp"
#include <iostream>

namespace xs = xsimd;

#if XSIMD_VERSION_MAJOR >= 9 && (XSIMD_WITH_NEON64 || XSIMD_WITH_NEON)
using number_type = float;
#else
using number_type = double;
#endif

int main(int argc, char *argv[]) {
#if XSIMD_VERSION_MAJOR < 8
  xs::batch<number_type, 4> a(1.5, 2.5, 3.5, 4.5);
  xs::batch<number_type, 4> b(2.5, 3.5, 4.5, 5.5);
#elif XSIMD_VERSION_MAJOR < 9
  xs::batch<number_type> a({1.5, 2.5, 3.5, 4.5});
  xs::batch<number_type> b({2.5, 3.5, 4.5, 5.5});
#else
  xs::batch<number_type> a{1.5, 2.5, 3.5, 4.5};
  xs::batch<number_type> b{2.5, 3.5, 4.5, 5.5};
#endif

  auto mean = (a + b) / 2;
  std::cout << mean << std::endl;
  return 0;
}
