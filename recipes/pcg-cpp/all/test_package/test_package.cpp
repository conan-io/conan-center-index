#include <pcg_random.hpp>

#include <random>
#include <iostream>

int main() {
    pcg32 rng(pcg_extras::seed_seq_from<std::random_device>{});
    std::cout << "RNG used: " << rng << "\n\n";
    return 0;
}
