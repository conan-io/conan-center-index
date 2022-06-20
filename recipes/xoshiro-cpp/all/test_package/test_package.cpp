#include <cstddef>
#include <iostream>
#include <random>
#include <cassert>
#include <type_traits>

#include "xoshiro-cpp/XoshiroCpp.hpp"

template <class N>
static void assert_and_print(N expected, N got) {
    std::cout << expected << " == " << got << '\n';
    if constexpr(std::is_integral_v<N>) {
        assert(expected == got);
    } else {
        assert(std::abs(expected - got) <= N(1.0e-6));
    }
}

int main() {
  using namespace XoshiroCpp;

  std::cout << "# Initialize with a default 64-bit seed\n";
  {
    Xoshiro256PlusPlus rng;
    for(uint64_t expected: {10656210946825422025ULL,
                            3029598875750717312ULL,
                            8253387787243700537ULL}) {
        assert_and_print(expected, rng());
    }
  }

  std::cout << "\n# Initialize with a 64-bit seed\n";
  {
    constexpr std::uint64_t seed = 777;

    Xoshiro256PlusPlus rng(seed);
    for(uint64_t expected: {2066146677187504009ULL,
                            6759878664999814329ULL,
                            16424726015236065913ULL}) {
        assert_and_print(expected, rng());
    }
  }

  std::cout << "\n# Initialize with a given state\n";
  {
    // poorly distributed
    constexpr std::uint64_t seed0 = 0;
    constexpr std::uint64_t seed1 = 0;
    constexpr std::uint64_t seed2 = 1;
    constexpr std::uint64_t seed3 = 1;
    constexpr Xoshiro256PlusPlus::state_type state = {seed0, seed1, seed2,
                                                      seed3};

    Xoshiro256PlusPlus rng(state);
    for(uint64_t expected: {8388608ULL,
                            8388625ULL,
                            598134325510176ULL}) {
        assert_and_print(expected, rng());
    }
  }

  std::cout
      << "\n# Initialize with a given state (SplitMix64 is used for entropy)\n";
  {
    // poorly distributed
    constexpr std::uint64_t seed0 = 0;
    constexpr std::uint64_t seed1 = 0;
    constexpr std::uint64_t seed2 = 1;
    constexpr std::uint64_t seed3 = 1;
    constexpr Xoshiro256PlusPlus::state_type state = {
        SplitMix64(seed0)(), SplitMix64(seed1)(), SplitMix64(seed2)(),
        SplitMix64(seed3)()};

    Xoshiro256PlusPlus rng(state);
    for(uint64_t expected: {17663883336656315162ULL,
                            13400192934578747583ULL,
                            6292764951643815248ULL}) {
        assert_and_print(expected, rng());
    }
  }

  std::cout << "\n# Generate double in the range of [0.0, 1.0)\n";
  {
    Xoshiro256PlusPlus rng(111);
    for(double expected: {0.608321,
                          0.963576,
                          0.128010}) {
        assert_and_print(expected, DoubleFromBits(rng()));
    }
  }
}
