#include "nonstd/byte.hpp"

#include <stdexcept>

using namespace nonstd;

int main()
{
    byte b1 = to_byte( 0x5a );  // to_byte() is non-standard, needed for pre-C++17
    byte b2 = to_byte( 0xa5 );

    byte r1 = b1 ^ b2; if( 0xff != to_integer( r1 )               ) throw std::exception();  // not (yet) standard, needs C++11
    byte r2 = b1 ^ b2; if( 0xff != to_integer<unsigned int>( r2 ) ) throw std::exception();
}
