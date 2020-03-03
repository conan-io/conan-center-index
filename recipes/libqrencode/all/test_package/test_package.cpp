#include <cstdlib>
#include <iostream>

#include "genqr.h"

int main()
{
    std::cout << "Generating QR code for the 'dummy.png' text and store to the dummy.png file\n";
    return genqr("dummy.png", "dummy.png");
}
