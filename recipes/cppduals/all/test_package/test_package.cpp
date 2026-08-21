// Smoke test for the packaged headers: f(x) = x*sin(x), f'(2) via dual.
#include <duals/dual>
#include <iostream>

int main()
{
  using namespace duals::literals;
  auto y = (2.0 + 1.0_e) * sin(2.0 + 1.0_e);
  std::cout << "f(2) = " << rpart(y) << ", f'(2) = " << dpart(y) << "\n";
  return 0;
}
