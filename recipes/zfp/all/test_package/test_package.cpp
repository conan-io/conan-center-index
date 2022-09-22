#include <iostream>

#include "zfp.h"

#if ZFP_VERSION_MAJOR < 1
#  include "zfparray2.h"
#else
#  include "zfp/array2.hpp"
#endif

template <class array2d>
inline double total(const array2d& u)
{
  double s = 0;
  const int nx = u.size_x();
  const int ny = u.size_y();
  for (int y = 1; y < ny - 1; y++)
    for (int x = 1; x < nx - 1; x++)
      s += u(x, y);
  return s;
}

int main(int argc, const char *argv[])
{
    const int nx = 100;
    const int ny = 100;
    const int cache = 4;
    const double rate = 64;
    zfp::array2d u(nx, ny, rate, 0, cache * 4 * 4 * sizeof(double));
    double sum = total(u);

    return 0;
}
