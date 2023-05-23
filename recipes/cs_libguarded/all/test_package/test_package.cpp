#include <iostream>
#ifndef CS_LIBGUARDED_1_3_0_LATER
  #include <libguarded/guarded.hpp>
#else
  #include <cs_plain_guarded.h>
#endif

int main() {
#ifndef CS_LIBGUARDED_1_3_0_LATER
  libguarded::guarded<int> g;
#else
  libguarded::plain_guarded<int> g;
#endif
  *g.lock() = 42;
  return 0;
}
