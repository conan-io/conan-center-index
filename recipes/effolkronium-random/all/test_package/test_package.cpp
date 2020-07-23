#include "effolkronium/random.hpp"

int main( ) {
  effolkronium::random_local random{ };
  auto val = random.get(-10, 10);
  return 0;
}
