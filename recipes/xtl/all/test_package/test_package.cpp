#include <iostream>
#include <xtl/xvariant.hpp>

int main(int argc, char *argv[]) {
  xtl::variant<int, float> v, w;

  v = 12;
  int i = xtl::get<int>(v);
  w = xtl::get<int>(v);

  std::cout << xtl::get<int>(v) << "\n";
  std::cout << xtl::get<int>(w) << "\n";

  return 0;
}
