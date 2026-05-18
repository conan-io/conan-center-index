#include <iostream>
#include <string>

#include <oapv/oapv.h>


int main (int argc, char *argv[])
{
    unsigned int version_num      = -1;
    const std::string version_str = oapv_version(&version_num);
    std::cout << "oapv_version reported version number: " << version_num << std::endl;
    std::cout << "oapv_version reported version string: " << version_str << std::endl;
    return EXIT_SUCCESS;
}
