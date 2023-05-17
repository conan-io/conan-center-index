#include <iostream>

#include <mgs/base64.hpp>

int main() {
  std::cout << mgs::base64::encode("Hello, World!") << std::endl;
}
