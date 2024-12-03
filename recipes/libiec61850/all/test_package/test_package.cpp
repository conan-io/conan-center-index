#include <iostream>
#include <format>
#include <cstdlib>

#include "libiec61850/iec61850_common.h"

int main(int argc, char **argv)
{
    std::cout << std::format("libiec61850 v{}\n", LibIEC61850_getVersionString());
    return 0;
}
