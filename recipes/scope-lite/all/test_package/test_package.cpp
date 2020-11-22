#include "nonstd/scope.hpp"

using namespace nonstd;

int count = 0;

namespace on { void exit() { ++count; } }

int main()
{
    { auto guard = make_scope_exit(  on::exit ); } // note: on_exit w/o &
    { auto guard = make_scope_exit( &on::exit ); } // note: &on_exit

    return !( count == 2 ); // 0: ok
}
