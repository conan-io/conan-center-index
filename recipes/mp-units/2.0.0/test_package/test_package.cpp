#include <mp-units/systems/si/si.h>
#include <mp-units/ostream.h>
#include <iostream>

using namespace mp_units;

constexpr auto avg_speed(QuantityOf<isq::length> auto d, QuantityOf<isq::time> auto t)
{
  return d / t;
}

int main()
{
  using namespace mp_units::si::unit_symbols;
  std::cout << "Average speed = " << avg_speed(240 * km, 2 * h) << '\n';
}
