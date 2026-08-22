#include "nonstd/ring_span.hpp"
#include <iostream>
#include <numeric>

template< typename T, size_t N >
inline size_t dim( T (&arr)[N] ) { return N; }

int main()
{
    double arr[]   = { 2.0 , 3.0, 5.0, };
    double coeff[] = { 0.25, 0.5, 0.25 };

    nonstd::ring_span<double> buffer( arr, arr + dim(arr), arr, dim(arr) );

    // new sample:
    buffer.push_back( 7.0 );

    if ( 5 != std::inner_product( buffer.begin(), buffer.end(), coeff, 0.0 ) )
        throw std::exception();
}
