///
/// @file   generate_n_primes1.cpp
/// @brief  Test n prime number generation.
///
/// Copyright (C) 2022 Kim Walisch, <kim.walisch@gmail.com>
///
/// This file is distributed under the BSD License. See the COPYING
/// file in the top level directory.
///

#include <primesieve.hpp>

#include <stdint.h>
#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>

using namespace primesieve;

// primes inside [0, 100]
const uint64_t small_primes[25] =
{
   2,  3,  5,  7, 11,
  13, 17, 19, 23, 29,
  31, 37, 41, 43, 47,
  53, 59, 61, 67, 71,
  73, 79, 83, 89, 97
};

// primes inside [18446744073709550681, 18446744073709551533]
const uint64_t large_primes[19] =
{
  18446744073709550681ull,
  18446744073709550717ull,
  18446744073709550719ull,
  18446744073709550771ull,
  18446744073709550773ull,
  18446744073709550791ull,
  18446744073709550873ull,
  18446744073709551113ull,
  18446744073709551163ull,
  18446744073709551191ull,
  18446744073709551253ull,
  18446744073709551263ull,
  18446744073709551293ull,
  18446744073709551337ull,
  18446744073709551359ull,
  18446744073709551427ull,
  18446744073709551437ull,
  18446744073709551521ull,
  18446744073709551533ull
};

void check(bool OK)
{
  std::cout << "   " << (OK ? "OK" : "ERROR") << "\n";
  if (!OK)
    std::exit(1);
}

int main()
{
  std::vector<uint64_t> primes;
  generate_n_primes(25, &primes);
  std::cout << "primes.size() = " << primes.size();
  check(primes.size() == 25);

  for (uint64_t i = 0; i < primes.size(); i++)
  {
    std::cout << "primes[" << i << "] = " << primes[i];
    check(primes[i] == small_primes[i]);
  }

  primes.clear();

  generate_n_primes(19, 18446744073709550672ull, &primes);
  std::cout << "primes.size() = " << primes.size();
  check(primes.size() == 19);

  for (uint64_t i = 0; i < primes.size(); i++)
  {
    std::cout << "primes[" << i << "] = " << primes[i];
    check(primes[i] == large_primes[i]);
  }

  std::string errorMsg;

  try
  {
    std::vector<uint16_t> primes16;
    generate_n_primes(10, (1 << 16) - 10, &primes16);
  }
  catch (const primesieve_error& e)
  {
    errorMsg = e.what();
  }

  std::cout << "Detect 16-bit overflow: " << errorMsg;
  check(!errorMsg.empty());

  std::cout << std::endl;
  std::cout << "All tests passed successfully!" << std::endl;

  return 0;
}
