#include <cstdlib>
#include <iostream>
#include <libconfig.h++>

int main()
{
    libconfig::Config cfg;

    cfg.setOptions(libconfig::Config::OptionFsync
    | libconfig::Config::OptionSemicolonSeparators
    | libconfig::Config::OptionColonAssignmentForGroups
    | libconfig::Config::OptionOpenBraceOnSeparateLine);
    return EXIT_SUCCESS;
}
