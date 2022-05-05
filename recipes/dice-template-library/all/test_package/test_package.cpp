#include <concepts>
#include <Dice/IntegralTemplatedTuple.hpp>
#include <ios>
#include <iostream>

template <int N> struct Wrapper { static constexpr int i = N; };

int main() {
  Dice::templateLibrary::IntegralTemplatedTuple<Wrapper, 0, 5> tup;
  std::cout << std::boolalpha << "tup.get<3>().i == 3: " << (tup.get<3>().i == 3) << std::endl;
}
