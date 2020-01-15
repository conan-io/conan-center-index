#include <iostream>
#include <cstdlib>

#include <pixman.h>
#include <pixman-version.h>

int main()
{
    std::cout << "pixman version: " << PIXMAN_VERSION_STRING << std::endl;
    return EXIT_SUCCESS;
}
