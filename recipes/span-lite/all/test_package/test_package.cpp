#include "nonstd/span.hpp"
#if span_CPP11_OR_GREATER
#include <array>
#endif
#include <vector>
#include <iostream>

std::ptrdiff_t size( nonstd::span<const int> spn )
{
    return spn.size();
}

int main()
{
    int arr[] = { 1, };

    std::cout <<
        "C-array:" << size( arr )
#if span_CPP11_OR_GREATER
        << " array:"  << size( std::array <int, 2>{ 1, 2, } )
#endif
     ;

    return 0;
}
