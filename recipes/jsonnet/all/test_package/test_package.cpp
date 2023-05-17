#include <libjsonnet++.h>

#include <iostream>

int main() {
  // C++ library
  jsonnet::Jsonnet j;
  if (!j.init()) {
    return 1;
  }
  std::cout << jsonnet::Jsonnet::version() << "\n";
  return 0;
}
