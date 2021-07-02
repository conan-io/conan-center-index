#include <units/physical/si/derived/speed.h>
#include <iostream>

int main()
{
  using namespace units::physical::si::literals;
  std::cout << "Speed = " << 240._q_km / 2_q_h << '\n';
}
