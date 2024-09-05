#include <iostream>
#if defined __has_include && __has_include(<limits>)
#  define HAVE_STDCXX_LIMITS 1
#endif
#include "Statistic.h"

int main(void) {
    statistic::Statistic<float, uint32_t, true> myStats;

    for (int i = 0; i < 10; i++) {
        myStats.add(i);
    }
    std::cout << myStats.count() << std::endl;
    std::cout << myStats.average() << std::endl;
    std::cout << myStats.variance() << std::endl;
    std::cout << myStats.minimum() << std::endl;
    std::cout << myStats.maximum() << std::endl;

    return 0;
}
