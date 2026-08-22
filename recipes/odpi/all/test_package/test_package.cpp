#include <cstdlib>
#include <iostream>

#include "dpi.h"

int main(void) {
    dpiVersionInfo versionInfo;
    dpiContext_getClientVersion(NULL, &versionInfo);
    std::cout << "ODPI Test Package executed with success." << std::endl;
    return EXIT_SUCCESS;
}
