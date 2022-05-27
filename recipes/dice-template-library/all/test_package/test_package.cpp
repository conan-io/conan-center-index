#include <concepts>
#include <Dice/template_library/IntegralTemplatedTuple.hpp>
#include <ios>
#include <iostream>

template <int N> struct Wrapper { static constexpr int i = N; };

int main() {
  Dice::template_library::IntegralTemplatedTuple<Wrapper, 0, 5> tup;
  std::cout << std::boolalpha << "tup.get<3>().i == 3: " << (tup.get<3>().i == 3) << std::endl;
}
