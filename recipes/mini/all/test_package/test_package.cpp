#include <iostream>

#include "mini/ini.h"

int main(void) {
    mINI::INIFile file("test_package.ini");

    std::cout << "mini test successful \n";
    return 0;
}
