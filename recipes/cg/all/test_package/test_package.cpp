#include "Cg/cg.h"

#include <iostream>

int main()
{
    std::cout << "Cg v" << cgGetString(CG_VERSION) << std::endl;
    return 0;
}
