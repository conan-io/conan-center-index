#include <iostream>
#include "dispenso/platform.h"


int main(void) {
    std::cout << DISPENSO_MAJOR_VERSION << "." << DISPENSO_MINOR_VERSION << std::endl;

    return EXIT_SUCCESS;
}
