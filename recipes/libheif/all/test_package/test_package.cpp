#include <iostream>
#include "libheif/heif.h"

int main() {
  std::cout << heif_get_version() << std::endl;
  return 0;
}
