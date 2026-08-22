#include <iostream>
#include <vector>

#include <libInterpolate/Interpolate.hpp>

int main(void)
{
  std::vector<double> x(2), y(2);

  x[0] = 0;
  x[1] = 1;
  y[0] = 10;
  y[1] = 20;

  _1D::LinearInterpolator<double> interp;
  interp.setData(x, y);

  std::cout << "f(0.5) = " << interp(0.5) << std::endl;

  return EXIT_SUCCESS;
}
