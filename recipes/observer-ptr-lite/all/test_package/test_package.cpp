#include "nonstd/observer_ptr.hpp"

#include <string>
#include <stdexcept>

using namespace nonstd;

void use( observer_ptr<int> p )
{
    if ( *p != 42 )
        throw std::exception();
}

int main()
{
    int a = 42;
    observer_ptr<int> p( &a );
    use( p );
}
