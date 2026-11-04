#include "xsimd/xsimd.hpp"
#include <iostream>

int main(int argc, char *argv[]) {
  namespace xs = xsimd;
  auto a = xs::broadcast(1.);
  auto b = xs::broadcast(2.);
  auto mean = (a + b) / 2.;
  std::cout << "Mean: " << mean << std::endl;
  return 0;
}
