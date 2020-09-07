#include <cstdlib>
#include <iostream>
#include <cairo.h>
#include <cairo-version.h>

int main()
{
    std::cout << "cairo version is " << cairo_version_string() << std::endl;
    return EXIT_SUCCESS;
}
