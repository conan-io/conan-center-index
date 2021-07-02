#include "nonstd/any.hpp"

#include <string>
#include <stdexcept>

using namespace nonstd;

int main()
{
    const std::string hello = "hello, world";

    any var;

    var =  'v' ; if( any_cast<char>( var ) != 'v' ) throw std::exception();
    var =   7  ; if( any_cast<int >( var ) !=  7  ) throw std::exception();
    var =  42L ; if( any_cast<long>( var ) != 42L ) throw std::exception();
    var = hello; if( any_cast<std::string>( var ) != hello ) throw std::exception();
}
