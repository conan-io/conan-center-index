#include "nonstd/bit.hpp"
#include <iostream>

using namespace nonstd;

int main()
{
    // Consecutive ones at the right in 0x17:
    if ( countr_one( 0x17u ) != 3 )
        throw std::exception();

    // Bit width of 0x13:
    if ( bit_width( 0x13u ) != 5 )
        throw std::exception();
}
