#include "fastPRNG.h"

#include <iostream>

int main() {
    fastPRNG::fastXS64 fastR;

    std::cout << fastR.xoshiro256p() << std::endl;

    return 0;
}
