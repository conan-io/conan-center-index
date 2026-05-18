#include <cstdlib>
#include <iostream>
#include "slang/util/VersionInfo.h"

using namespace slang;

int main(void) {
    std::cout << "Slang Verilog Version: " << VersionInfo::getMajor() << "."
              << VersionInfo::getMinor() << "."
              << VersionInfo::getPatch() << " ("
              << VersionInfo::getHash() << ")" << std::endl;

    return EXIT_SUCCESS;
}
