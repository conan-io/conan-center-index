#include "nonstd/scope.hpp"

using namespace nonstd;

int count = 0;

namespace on { void exit() { ++count; } }

int main()
{
#if scope_USE_POST_CPP98_VERSION
    { auto guard = make_scope_exit(  on::exit ); }          // note: on_exit w/o &
    { auto guard = make_scope_exit( &on::exit ); }          // note: &on_exit
#else
    { scope_exit guard = make_scope_exit(  on::exit ); }    // note: on_exit w/o &
    { scope_exit guard = make_scope_exit( &on::exit ); }    // note: &on_exit
#endif

    return !( count == 2 ); // 0: ok
}
