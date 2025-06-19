#include <cryptopp/cryptlib.h>
#include <iostream>

int main() {
  std::cout << "CryptoPP LibraryVersion() = " << CryptoPP::LibraryVersion() << std::endl;
  std::cout << "CryptoPP HeaderVersion() = " << CryptoPP::HeaderVersion() << std::endl;
  return 0;
}
