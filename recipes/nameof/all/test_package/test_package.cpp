#include <nameof.hpp>

#include <cstdlib>

struct SomeStruct {};

SomeStruct structvar;

int main() {
  constexpr auto name = NAMEOF(structvar);
  static_assert("structvar" == name);

  auto res1 = NAMEOF(structvar);
  auto res2 = NAMEOF(::structvar);

  bool success = (res1 == "structvar") && (res2 == "structvar");

  return success ? EXIT_SUCCESS : EXIT_FAILURE;
}
