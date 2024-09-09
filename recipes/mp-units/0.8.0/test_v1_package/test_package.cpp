#include <units/isq/si/length.h>
#include <units/isq/si/speed.h>
#include <units/isq/si/time.h>
#include <units/quantity_io.h>
#include <iostream>

using namespace units;

template<isq::Length Length, isq::Time Time>
constexpr auto avg_speed(Length d, Time t)
{
  return d / t;
}

int main()
{
  using namespace units::isq::si::references;
  std::cout << "Average speed = " << avg_speed(240 * km, 2 * h) << '\n';
}
