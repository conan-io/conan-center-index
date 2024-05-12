#include <iostream>
#include <cstdlib>

#include "ocilib.hpp"

using namespace ocilib;

int main(void)
{
    try
    {
        std::cout << "OCILIB Version: ";
        std::cout << OCILIB_MAJOR_VERSION << ".";
        std::cout << OCILIB_MINOR_VERSION << ".";
        std::cout << OCILIB_REVISION_VERSION << std::endl;

        Environment::Initialize();
    }
    catch (...)
    {
    }

    Environment::Cleanup();

    return EXIT_SUCCESS;
}
