#include <cstdlib>
#include <iostream>

#include "nats/nats.h"


int main() {
    std::cout << "NATS Version: " << nats_GetVersion() << std::endl;
    return EXIT_SUCCESS;
}
