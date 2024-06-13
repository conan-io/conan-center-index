#include <dump.hpp>

#include <iostream>
#include <ostream>
#include <vector>

int main() {
  std::clog << std::endl;

  std::vector<std::vector<int>> my_vector{{3, 5, 8, 9, 7}, {9, 3, 2, 3, 8}};
  CPP_DUMP(my_vector);

  std::clog << std::endl;
}
