#include <iostream>

#include <packio/packio.h>

int main(int, char **) {
  auto io = packio::net::io_context();
  std::cout << "Test package successful\n";
  return 0;
}
