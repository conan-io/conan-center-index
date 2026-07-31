#include <iostream>
#include <yojimbo.h>

int main() {
  uint8_t buffer[10] = {0};
  yojimbo_random_bytes(buffer, sizeof(buffer));
  std::cout << "Yojimbo random byte: " << buffer[1] << std::endl;
  return 0;
}
