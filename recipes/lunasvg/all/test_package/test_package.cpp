#ifdef LUNASVG_BEFORE_3_0_0
#include "lunasvg.h"
#else
#include "lunasvg/lunasvg.h"
#endif
#include <iostream>

int main() {
  auto mat = lunasvg::Matrix();

  std::cout << mat.a << " " << mat.b << " " << mat.c << " " << mat.d << " " << mat.e << " " << mat.f << std::endl;

  return 0;
}
