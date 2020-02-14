#include <iostream>
#include <libguarded/guarded.hpp>

int main() {
  libguarded::guarded<int> g;
  *g.lock() = 42;
  return 0;
}
