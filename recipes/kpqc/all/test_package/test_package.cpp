#include <cstdlib>

#include "kpqc/kpqc.hpp"


int main() {
    const auto& algorithm = kpqc::ntruplus::ntruplus768();
    const auto keys = algorithm.generate_key_pair();
    const auto encapsulated = algorithm.encapsulate(keys.public_key);
    const auto shared_secret = algorithm.decapsulate(encapsulated.ciphertext, keys.secret_key);
    return shared_secret == encapsulated.shared_secret ? EXIT_SUCCESS : EXIT_FAILURE;
}
