#include <iostream>

#include <units.h>

using namespace units::literals;
using namespace units::length;
#ifndef UNITS_NEW_API
using namespace units::math;
#endif

int main()
{
#ifdef UNITS_NEW_API
  const auto a = 3.0_m;
  const auto b = 4.0_m;
  const meters<double> c = units::sqrt(units::pow<2>(a) + units::pow<2>(b));
#else
  meter_t a = 3_m;
  meter_t b = 4_m;
  meter_t c = sqrt(pow<2>(a) + pow<2>(b)); // Pythagorean threorem.
#endif
  std::cout << c << std::endl; // prints: "5 m"
}
