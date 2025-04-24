#include <cstdlib>
#include <iostream>
#include "ace/ACE.h"

int main(void)
{
    std::cout << "ACE major version: " << ACE::major_version() << std::endl;
    std::cout << "ACE minor version: " << ACE::minor_version() << std::endl;
    std::cout << "ACE micro version: " << ACE::micro_version() << std::endl;
    std::cout << "Compiled by: " << ACE::compiler_name() << " "
              << ACE::compiler_major_version() << "."
              << ACE::compiler_minor_version() << "."
              << ACE::compiler_beta_version()
              << std::endl;

    return EXIT_SUCCESS;
}
