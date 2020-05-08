#include "nonstd/expected.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

using nonstd::expected;

using ErrorInfo = expected<int, std::string>;

ErrorInfo to_int( char const * const text )
{
    char * pos = NULL;
    const int value = static_cast<int>( strtol( text, &pos, 0 ) );

    return pos == text ? nonstd::make_unexpected(std::string("Failed to convert '") + text + std::string("' to int")) : ErrorInfo(value);
}

int main( int argc, char * argv[] )
{
    const char * text = argc > 1 ? argv[1] : "42";

    auto val = to_int( text );

    if ( val ) std::cout << "'" << text << "' is " << val.value() << std::endl;
    else      std::cout << "'" << text << "' isn't a number. Error: " << val.error() << std::endl;
}

// cl -nologo -W3 -EHsc -I../include to_int.cpp && to_int x1
// g++ -Wall -Wextra -std=c++03 -I../include -o to_int.exe to_int.cpp && to_int x1
