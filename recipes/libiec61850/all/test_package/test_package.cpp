#include <iostream>
#include <cstdlib>

#include "libiec61850/iec61850_common.h"

int main(int argc, char **argv)
{
    std::cout << "libiec61850 v" << LibIEC61850_getVersionString() << std::endl;
    return 0;
}
