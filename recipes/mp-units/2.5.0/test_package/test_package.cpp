#include <mp-units/compat_macros.h>

#if MP_UNITS_HOSTED
#include <mp-units/ext/format.h>
#ifdef MP_UNITS_IMPORT_STD
import std;
#else
#include <iostream>
#endif
#endif

#ifdef MP_UNITS_MODULES
import mp_units;
#else
#include <mp-units/systems/isq.h>
#include <mp-units/systems/si.h>
#endif

using namespace mp_units;

constexpr QuantityOf<MP_UNITS_IS_VALUE_WORKAROUND(isq::speed)> auto avg_speed(
  QuantityOf<MP_UNITS_IS_VALUE_WORKAROUND(isq::distance)> auto d,
  QuantityOf<MP_UNITS_IS_VALUE_WORKAROUND(isq::duration)> auto t)
{
  return d / t;
}

int main()
{
  using namespace mp_units::si::unit_symbols;
#if MP_UNITS_HOSTED
  std::cout << MP_UNITS_STD_FMT::format("Average speed = {}\n", avg_speed(240 * km, 2 * h));
#else
  [[maybe_unused]] auto value = avg_speed(240 * km, 2 * h);
#endif
}
