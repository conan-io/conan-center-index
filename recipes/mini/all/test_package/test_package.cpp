#include <iostream>

#include "mini/ini.h"

int main(void) {
    mINI::INIFile file("test_package.ini");

    mINI::INIStructure ini;

    ini["things"]["chairs"] = "20";
    ini["things"]["balloons"] = "100";

    file.generate(ini);
}
