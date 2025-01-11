#include <symengine/constants.h>
#include <symengine/expression.h>
#include <symengine/integer.h>
#include <symengine/mul.h>
#include <symengine/mp_class.h>
#include <symengine/parser.h>

#include <string>
#include <iostream>

int main() {
  SymEngine::Expression pi_by_12 =
      SymEngine::div(SymEngine::pi, SymEngine::integer(12));
  std::cout << pi_by_12 << std::endl;
  std::cout << SymEngine::mp_perfect_power_p(SymEngine::integer_class("9")) << std::endl;
  std::string input = "123.0";
  auto parsed_value = SymEngine::parse(input, true);

  return 0;
}
