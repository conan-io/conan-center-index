#include <iostream>
#include "aom/aom_codec.h"

int main() {
  std::cout << "Version: " << aom_codec_version_str() << std::endl;
  return 0;
}
