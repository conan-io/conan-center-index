#include <cstdlib>
#include <iostream>

#include "LIEF/LIEF.hpp"
#include "LIEF/version.h"

int main()
{
    std::cout << LIEF_NAME << HUMAN_VERSION;

    LIEF::ELF::Binary* b = nullptr;
    return EXIT_SUCCESS;
}
