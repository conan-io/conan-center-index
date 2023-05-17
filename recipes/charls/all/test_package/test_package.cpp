#include <charls/charls.h>

#include <iostream>

int main() {
  std::cout << charls_get_version_string() << '\n';

  return 0;
}
