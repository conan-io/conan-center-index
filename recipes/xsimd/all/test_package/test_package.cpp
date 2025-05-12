#include "xsimd/xsimd.hpp"
#include <iostream>

int main(int argc, char *argv[]) {
  namespace xs = xsimd;
#if XSIMD_VERSION_MAJOR < 8
  xs::batch<double, 2> a(1., 1.);
  xs::batch<double, 2> b(2., 2.);
#else
  auto a = xs::broadcast(1.);
  auto b = xs::broadcast(2.);
#endif

  auto mean = (a + b) / 2.;
  std::cout << "Mean: " << mean << std::endl;
  return 0;
}
