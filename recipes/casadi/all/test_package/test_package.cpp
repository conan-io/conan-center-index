#include <casadi/casadi.hpp>

#include <iostream>

#ifdef CASADI_STATIC_PLUGINS
// Statically linked plugins are not dlopen'ed; register them by hand
extern "C" void casadi_load_nlpsol_sqpmethod();
extern "C" void casadi_load_conic_qrqp();
#endif

int main() {
  using namespace casadi;
#ifdef CASADI_STATIC_PLUGINS
  casadi_load_nlpsol_sqpmethod();
  casadi_load_conic_qrqp();
#endif
  // Symbolic core: AD on a small expression
  SX x = SX::sym("x", 2);
  SX f = x(0) * x(0) + 3 * x(1);
  Function grad("grad", {x}, {gradient(f, x)});
  DM g = grad(DM({1.0, 2.0}))[0];
  std::cout << "grad = " << g << std::endl;
  if (fabs(double(g(0)) - 2.0) > 1e-12 || fabs(double(g(1)) - 3.0) > 1e-12) return 1;

  // First-party plugin (loaded at runtime): sqpmethod with the built-in qrqp QP solver
  MX y = MX::sym("y");
  Function solver = nlpsol("solver", "sqpmethod", {{"x", y}, {"f", (y - 1) * (y - 1)}},
                           {{"qpsol", "qrqp"}, {"print_time", false}, {"print_iteration", false},
                            {"print_header", false}, {"qpsol_options", Dict{{"print_iter", false}}}});
  DMDict res = solver(DMDict{{"x0", 0}});
  std::cout << "x* = " << res["x"] << std::endl;
  if (fabs(double(res["x"]) - 1.0) > 1e-6) return 1;
  return 0;
}
