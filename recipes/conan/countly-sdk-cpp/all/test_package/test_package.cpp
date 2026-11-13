#include "countly.hpp"

#include <iostream>

int main() {
  (void)cly::Countly::getInstance();
  cly::Event event("test_package", 1);
  event.addSegmentation("source", "conan");
  std::cout << event.serialize() << std::endl;
  return 0;
}
