#include <iostream>
#include <cstdlib>

#include <ImfHeader.h>

int main (int argc, char *argv[])
{
    Imf::Header header;
    std::cout << "Test: " << header.screenWindowWidth() << std::endl;
    return EXIT_SUCCESS;
}
