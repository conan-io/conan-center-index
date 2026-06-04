#include <iostream>
#include <xtl/xoptional.hpp>

int main(int argc, char *argv[]) {
  xtl::xoptional<int, bool> v, w;

  w = v.value_or(0);
  v = 12;

  std::cout << v.value() << "\n";
  std::cout << w.value() << "\n";

  return 0;
}
