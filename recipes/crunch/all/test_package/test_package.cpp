#include <iostream>

#include "crnlib.h"

int main(int argc, const char* argv[])
{
    std::cout << "Test string: " << crn_get_format_string(crn_format::cCRNFmtDXT1) << std::endl;
    return 0;
}
