#include <iostream>
#include <keystone/keystone.h>

int main()
{
    unsigned int major = 0, minor = 0;
    ks_version(&major, &minor);
    std::cout << "Keystone version: " << major << "." << minor << std::endl;
    return EXIT_SUCCESS;
}
