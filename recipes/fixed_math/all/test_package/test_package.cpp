#include <utility>

#include "fixedmath/fixed_math.hpp"
#include "fixedmath/iostream.h"

using fixedmath::fixed_t;
using fixedmath::operator""_fix;

// fixed and all functionality is constexpr so You can declare constants see features [1]
inline constexpr fixed_t foo_constant{fixedmath::fobj::tan(15 * fixedmath::phi / 180)};

constexpr fixed_t my_function(fixed_t value) {
  using namespace fixedmath;
  // You can use funcioons or function objects
  return foo_constant + fobj::sin(value) / (1.41_fix - 2 * func::cos(value) / 4);
}

int main() {
  // converting to/from fixed_t
  // construction from other arithmetic types is explicit
  fixed_t val1{3.14};
  fixed_t val2{3u};

  //- there is no implicit assignment from other types
  float   some_float{3.14f};
  fixed_t some_fixed;
  some_fixed = fixed_t{some_float};

  //- converting to other arithmetic types coud be done with static cast and is explicit
  double some_double(some_fixed);

  // for constant values postfix operator _fix may be used
  some_fixed  = some_float * 2.45_fix;  // operation with float is promoted to fixed_t
  some_double = 4.15 * some_fixed;      // operation with double is promoted to double

  std::cout << some_double << " " << my_function(some_fixed) << std::endl;
}
