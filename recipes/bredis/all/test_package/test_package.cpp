#include <cstdlib>
#include <iostream>

#include "bredis/Connection.hpp"
#include "bredis/MarkerHelpers.hpp"

int main(int argc, const char **argv) {
  // Basic test avoiding any kind of access to network layer
  bredis::bredis_category category;
  std::cout << category.name() << '\n';
  return 0;
}
