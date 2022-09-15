#include "xsimd/xsimd.hpp"
#include <iostream>

namespace xs = xsimd;

int main(int argc, char *argv[]) {
#if XSIMD_VERSION_MAJOR < 8
  xs::batch<double, 4> a(1.5, 2.5, 3.5, 4.5);
  xs::batch<double, 4> b(2.5, 3.5, 4.5, 5.5);
#elif XSIMD_VERSION_MAJOR < 9
  xs::batch<double> a({1.5, 2.5, 3.5, 4.5});
  xs::batch<double> b({2.5, 3.5, 4.5, 5.5});
#else
  xs::batch<double, xs::default_arch> a{1.5, 2.5, 3.5, 4.5};
  xs::batch<double, xs::default_arch> b{2.5, 3.5, 4.5, 5.5};
#endif

  auto mean = (a + b) / 2;
  std::cout << mean << std::endl;
  return 0;
}
