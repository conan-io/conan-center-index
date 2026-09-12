#define TFHE_DISABLE_NOISE

#include <cstdlib>
#include <random>

#include "primitive.hpp"
#include "tfhe/ciphertext.hpp"
#include "tfhe/params.hpp"
#include "tfhe/runtime.hpp"

using Torus = ModTorus<32>;
using Lwe = lwe_params<tlwe_core_params<Torus, 630>, noise_params<15>>;

int main() {
  std::mt19937 eng{0};
  Runtime<Lwe> runtime(eng);

  TLWE<Torus, Lwe::n> ct = runtime.encrypt(Torus(1u, 4u));
  Torus plaintext = runtime.decrypt(ct);

  return plaintext == Torus(1u, 4u) ? EXIT_SUCCESS : EXIT_FAILURE;
}
