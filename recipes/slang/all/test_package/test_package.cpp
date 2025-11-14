#include <cstdlib>
#include <iostream>
#include "slang/util/VersionInfo.h"

using namespace slang;

int main(void) {
    std::cout << VersionInfo::getMajor() << std::endl;
    std::cout << VersionInfo::getMinor() << std::endl;
    std::cout << VersionInfo::getPatch() << std::endl;
    std::cout << VersionInfo::getHash() << std::endl;

    return EXIT_SUCCESS;
}
