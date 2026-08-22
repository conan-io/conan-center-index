#include <hipony/enumerate.hpp>

#include <array>
#include <iostream>

int main() {
  std::array<int, 6> array{0, 1, 2, 3, 4, 5};
  for (auto &&item : hipony::enumerate(array)) {
    std::cout << item.index << ' ' << item.value << '\n';
  }
}
