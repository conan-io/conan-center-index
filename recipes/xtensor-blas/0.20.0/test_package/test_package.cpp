#include "xtensor-blas/xlinalg.hpp"
#include "xtensor/xarray.hpp"
#include <iostream>

int main(int argc, char *argv[]) {
  xt::xarray<double> a = {{3, 2, 1}, {0, 4, 2}, {1, 3, 5}};
  auto d = xt::linalg::det(a);
  std::cout << d << std::endl; // 42.0
  return 0;
}
