#include <iostream>
#include <cstdlib>

#include <oapv/oapv.h>


int main (int argc, char *argv[])
{
    // Validate at least the header is found
    oapvd_cdesc testvar {1};
    std::cout << "Test: " << testvar.threads << std::endl;
    return EXIT_SUCCESS;
}
