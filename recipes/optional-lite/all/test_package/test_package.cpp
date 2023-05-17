#include "nonstd/optional.hpp"

#include <cstdlib>
#include <iostream>

using nonstd::optional;
using nonstd::nullopt;

optional<int> to_int( char const * const text )
{
    char * pos = NULL;
    const int value = static_cast<int>( strtol( text, &pos, 0 ) );

    return pos == text ? nullopt : optional<int>( value );
}

int main( int argc, char * argv[] )
{
    const char * text = argc > 1 ? argv[1] : "42";

    optional<int> oi = to_int( text );

    if ( oi ) std::cout << "'" << text << "' is " << *oi << std::endl;
    else      std::cout << "'" << text << "' isn't a number" << std::endl;
}

// cl -nologo -W3 -EHsc -I../include to_int.cpp && to_int x1
// g++ -Wall -Wextra -std=c++03 -I../include -o to_int.exe to_int.cpp && to_int x1
