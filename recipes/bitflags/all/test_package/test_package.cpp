#include "bitflags/bitflags.hpp"
#include <cassert>
#include <iostream>

BEGIN_BITFLAGS(Flags)
FLAG(none)
FLAG(flag_a)
FLAG(flag_b)
FLAG(flag_c)
END_BITFLAGS(Flags)

DEFINE_FLAG(Flags, none)
DEFINE_FLAG(Flags, flag_a)
DEFINE_FLAG(Flags, flag_b)
DEFINE_FLAG(Flags, flag_c)

int main() {
  std::cout << +Flags::none.bits << " - " << Flags::none.name << '\n';
  std::cout << +Flags::flag_a.bits << " - " << Flags::flag_a.name << '\n';
  std::cout << +Flags::flag_b.bits << " - " << Flags::flag_b.name << '\n';
  std::cout << +Flags::flag_c.bits << " - " << Flags::flag_c.name << '\n';

  const auto flags = Flags::flag_a | Flags::flag_b;

  assert(flags & Flags::flag_a);
  assert(!(flags & Flags::flag_c));
}
