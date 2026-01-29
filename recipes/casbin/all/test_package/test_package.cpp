#include <cstdlib>
#include <iostream>

#include <casbin/casbin.h>

int main() {
  std::cout << casbin::Join({"Test", "OK"}, " ") << std::endl;
  return EXIT_SUCCESS;
}
