#include <iostream>

#include <libField/Field.hpp>

int main(void)
{
  Field<double, 1> f(5);
  f.setCoordinateSystem(Uniform(0, 10));
  f.set_f([](auto x) { return x[0] * x[0]; });

  std::cout << f << std::endl;

  return EXIT_SUCCESS;
}
