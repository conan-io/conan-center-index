#include "nonstd/any.hpp"

#include <cassert>
#include <string>

using namespace nonstd;

int main()
{
    std::string hello = "hello, world";

    any var;

    var =  'v' ; assert( any_cast<char>( var ) == 'v' );
    var =   7  ; assert( any_cast<int >( var ) ==  7  );
    var =  42L ; assert( any_cast<long>( var ) == 42L );
    var = hello; assert( any_cast<std::string>( var ) == hello );
}

// cl -nologo -EHsc -I../include 01-basic.cpp && 01-basic
// g++ -Wall -I../include -o 01-basic 01-basic.cpp && 01-basic