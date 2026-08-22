#include <vectorial/vectorial.h>

#include <iostream>

int main() {
  vectorial::vec4f v = vectorial::normalize(vectorial::vec4f(1, 2, 3, 4));
  std::cout << v.z() << std::endl;
  return 0;
}
