#include <primesieve.hpp>

#include <cstdint>
#include <iostream>
#include <vector>

int main() {
  std::vector<uint64_t> primes;
  primesieve::generate_n_primes(5, &primes);
  std::cout << "First 5 primes: ";
  for (const auto prime : primes) {
    std::cout << prime << ' ';
  }
  std::cout << '\n';
}
