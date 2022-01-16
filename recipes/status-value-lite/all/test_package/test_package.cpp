#include "nonstd/status_value.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

using namespace nonstd;

auto to_int( char const * const text ) -> status_value<std::string, int>
{
    char * pos = nullptr;
    const int value = static_cast<int>( strtol( text, &pos, 0 ) );

    if ( pos != text ) return { "Excellent", value };
    else               return { std::string("'") + text + "' isn't a number" };
}

int main( int argc, char * argv[] )
{
    const char * text = argc > 1 ? argv[1] : "42";

    status_value<std::string, int> svi = to_int( text );

    if ( svi ) std::cout << svi.status() << ": '" << text << "' is " << *svi << ", ";
    else       std::cout << "Error: " << svi.status();
}
