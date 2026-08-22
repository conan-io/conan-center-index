#include <iostream>

#include <units.h>

using namespace units::literals;
using namespace units::length;
using namespace units::math;

int main()
{
  meter_t a = 3_m;
  meter_t b = 4_m;
  meter_t c = sqrt(pow<2>(a) + pow<2>(b)); // Pythagorean threorem.
  std::cout << c << std::endl; // prints: "5 m"
}
