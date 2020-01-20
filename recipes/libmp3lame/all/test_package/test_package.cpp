#include <cstdlib>
#include <iostream>
#include "lame/lame.h"

int main()
{
    std::cout << get_lame_version() << std::endl;
    return EXIT_SUCCESS;
}
