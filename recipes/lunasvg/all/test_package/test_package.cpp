#include "lunasvg.h"
#include <iostream>

int main() {
  auto mat = lunasvg::Matrix();

  std::cout << mat.a << " " << mat.b << " " << mat.c << " " << mat.d << " " << mat.e << " " << mat.f << std::endl;

  return 0;
}
