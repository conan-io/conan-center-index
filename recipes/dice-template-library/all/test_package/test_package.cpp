#include <concepts>
#include <Dice/template-library/integral_templated_tuple.hpp>
#include <ios>
#include <iostream>

template <int N> struct Wrapper { static constexpr int i = N; };

int main() {
  Dice::template_library::IntegralTemplatedTuple<Wrapper, 0, 5> tup;
  std::cout << std::boolalpha << "tup.get<3>().i == 3: " << (tup.get<3>().i == 3) << std::endl;
}
