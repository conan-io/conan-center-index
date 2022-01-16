#include "nonstd/status_value_cpp98.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

using namespace nonstd;

status_value<std::string, int> to_int( char const * const text )
{
    char * pos = NULL;
    const int value = static_cast<int>( strtol( text, &pos, 0 ) );

    if ( pos != text ) return status_value<std::string, int>( "Excellent", value );
    else               return status_value<std::string, int>( std::string("'") + text + "' isn't a number" );
}

int main( int argc, char * argv[] )
{
    const char * text = argc > 1 ? argv[1] : "42";

    status_value<std::string, int> svi = to_int( text );

    if ( svi ) std::cout << svi.status() << ": '" << text << "' is " << *svi << ", ";
    else       std::cout << "Error: " << svi.status();
}
