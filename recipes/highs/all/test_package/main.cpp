#include <cstdlib>
#include <iostream>
#include "highs/Highs.h"


int main() {
    std::cout << "HiGHS Version: " << highsVersion() << std::endl;
    return EXIT_SUCCESS;
}
