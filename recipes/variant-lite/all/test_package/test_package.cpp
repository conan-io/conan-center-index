#include "nonstd/variant.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

using nonstd::variant;

typedef variant<int, std::string> ErrorInfo;

ErrorInfo to_int( char const * const text )
{
    char * pos = NULL;
    const int value = static_cast<int>( strtol( text, &pos, 0 ) );

    return pos == text ? ErrorInfo(std::string("Failed to convert '") + text + std::string("' to int")) : ErrorInfo(value);
}

int main( int argc, char * argv[] )
{
    const char * text = argc > 1 ? argv[1] : "42";

    ErrorInfo val = to_int( text );

    if ( nonstd::get_if<int>(&val) ) std::cout << "'" << text << "' is " << nonstd::get<int>(val) << std::endl;
    else std::cout << "'" << text << "' isn't a number. Error: " << nonstd::get<std::string>(val) << std::endl;
}

// cl -nologo -W3 -EHsc -I../include to_int.cpp && to_int x1
// g++ -Wall -Wextra -std=c++03 -I../include -o to_int.exe to_int.cpp && to_int x1
