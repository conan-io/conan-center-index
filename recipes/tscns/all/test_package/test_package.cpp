#include <iostream>

#include "tscns.h"

int main() {
    TSCNS tn;
    tn.init();

    std::cout << tn.getTscGhz() << std::endl;

    uint64_t count = (tn.rdns() % 100u) + 1;

    uint64_t tsc1 = tn.rdtsc();
    int total = 0;
    while (count-- > 0) {
        total += count;
    }
    uint64_t tsc2 = tn.rdtsc();

    std::cout << (tn.tsc2ns(tsc2) - tn.tsc2ns(tsc1)) << " ns" << std::endl;

    return 0;
}
