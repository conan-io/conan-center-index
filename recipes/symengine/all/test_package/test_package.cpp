#include <symengine/constants.h>
#include <symengine/expression.h>
#include <symengine/integer.h>
#include <symengine/mul.h>

#include <iostream>

int main() {
  SymEngine::Expression pi_by_12 =
      SymEngine::div(SymEngine::pi, SymEngine::integer(12));
  std::cout << pi_by_12 << std::endl;
  return 0;
}
