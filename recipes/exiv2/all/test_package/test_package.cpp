#include <exiv2/exiv2.hpp>
#include <iostream>

int main() {
  std::cout << Exiv2::versionString() << std::endl;
  return 0;
}
