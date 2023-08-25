#include <cstdlib>
#include <iostream>
#include <vir/simd.h>

namespace stdx = vir::stdx;

template <class T, class A>
std::ostream& operator<<(std::ostream& s, const stdx::simd<T, A>& v) {
    s << '[' << v[0];
    for (std::size_t i = 1; i < v.size(); ++i) {
        s << ", " << v[i];
    }
    return s << ']';
}

int main(void) {
    
    using floatv = stdx::simd<float, stdx::simd_abi::fixed_size<8>>;
    const floatv a{5};
    
    std::cout << a * 3<< std::endl;

    return EXIT_SUCCESS;
}
