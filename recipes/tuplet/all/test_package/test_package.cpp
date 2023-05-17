#include <iostream>
#include <tuplet/tuple.hpp>

int main() {
  auto print = [](auto&&... args) { ((std::cout << args << '\n'), ...); };
  tuplet::apply(print, tuplet::tuple{1, 2, "Hello, world!"});
  return 0;
}
