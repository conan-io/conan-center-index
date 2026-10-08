#include <casadi/casadi.hpp>
#include <iostream>

#ifdef CASADI_STATIC_PLUGINS
// Statically linked plugins are not dlopen'ed; register them by hand
extern "C" void casadi_load_interpolant_linear();
#endif

int main() {
#ifdef CASADI_STATIC_PLUGINS
  casadi_load_interpolant_linear();
#endif
  std::vector<double> grid = {0, 1, 2}, values = {0, 10, 20};
  casadi::Function f = casadi::interpolant("f", "linear", {grid}, values);
  std::cout << f(casadi::DM(1.5)) << std::endl;
  return 0;
}
