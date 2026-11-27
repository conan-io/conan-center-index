#include <ptn/patternia.hpp>

#include <cstdio>
#include <cstring>

int main() {
  using namespace ptn;

  const char *result = match(42)
                       | on(lit(0) >> "zero", _ >> "other");

  std::puts(result);
  return std::strcmp(result, "other") == 0 ? 0 : 1;
}
