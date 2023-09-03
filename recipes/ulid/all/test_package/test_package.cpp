#include <cstdlib>
#include <iostream>

#include "ulid/ulid.h"

int main(void)
{
    std::cout << ulid::generate().str();

    return EXIT_SUCCESS;
}
