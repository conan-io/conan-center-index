#include <mathfu/vector.h>

#include <iostream>

int main() {
  mathfu::Vector<float, 3> v1(1.0f, 2.0f, 3.0f);
  mathfu::Vector<float, 3> v2(3.0f, 2.5f, 0.5f);
  mathfu::Vector<float, 3> v3 = v1 + v2;
  std::cout << v3.Length() << std::endl;
  return 0;
}
