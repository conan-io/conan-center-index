#include <iostream>

#include "choc/platform/choc_Platform.h"

int main(void) {
    std::cout << CHOC_OPERATING_SYSTEM_NAME << '\n';

    return EXIT_SUCCESS;
}
