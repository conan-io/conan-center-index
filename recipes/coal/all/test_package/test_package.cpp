#include "coal/math/transform.h"
#include <iostream>

int main() {
  coal::Transform3s t1;
  t1.setTranslation(coal::Vec3s::Random());
  const auto translation = t1.translation();

  std::cout << "Translation T1:\n" << translation << std::endl;

  return EXIT_SUCCESS;
}
