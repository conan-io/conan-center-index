#include "nonstd/string_view.hpp"
#include <iostream>

#if nssv_CPP11_OR_GREATER
using namespace nonstd::literals;
#if nssv_CPP14_OR_GREATER
using namespace std::literals;
#endif
#endif
using namespace nonstd;
    
void write( string_view sv )
{
    std::cout << sv;
}

int main()
{
    write( "hello"     );   // C-string
#if nssv_CPP11_OR_GREATER
    write( ", "_sv );   // nonstd::string_view
#if nssv_CPP14_OR_GREATER
    write( "world!"s       );   // std::string
#endif
#endif
}
