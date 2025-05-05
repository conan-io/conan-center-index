#include "cryptopp/cryptlib.h"
#include "cryptopp/osrng.h" // AutoSeededRandomPool

#include <stdio.h>

int main() {
  printf("CryptoPP version: %d\n", CRYPTOPP_VERSION);

  CryptoPP::AutoSeededRandomPool rng;
  printf("This is a random number from CryptoPP: %d\n", rng.GenerateByte());

  return 0;
}
