#include <etl/version.h>
#include <iostream>

int main() {
  std::cout << "etl version: " << etl::traits::version_string << std::endl;
  return 0;
}