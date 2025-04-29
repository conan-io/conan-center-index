#include <cstdlib>
#include <iostream>

#ifndef ACE_LACKS_ACE_TOKEN
#include "ace/ACE.h"
#endif

#include "tao/Version.h"

/* see https://comp.soft-sys.ace.narkive.com/J3xRPy8I/ace-link-error */
int main(int argc, char *argv[])
{

#ifndef ACE_LACKS_ACE_TOKEN
    std::cout << "ACE major version: " << ACE::major_version() << std::endl;
    std::cout << "ACE minor version: " << ACE::minor_version() << std::endl;
    std::cout << "ACE micro version: " << ACE::micro_version() << std::endl;
#else
    std::cout << "ACE was compiled with ace_for_tao" << std::endl;
#endif
    std::cout << "TAO version: " << TAO_VERSION << std::endl;

#ifndef ACE_LACKS_ACE_TOKEN
    std::cout << "Compiled by: " << ACE::compiler_name() << " "
              << ACE::compiler_major_version() << "."
              << ACE::compiler_minor_version() << "."
              << ACE::compiler_beta_version()
              << std::endl;
#endif

    return EXIT_SUCCESS;
}
