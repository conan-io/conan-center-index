// This source file should check the imported headers and do the simple things,
// like querying library version. It doesn't intended to do some lengthy work
// or running library tests - just only check that package is properly created.
// See docs for details:
// https://docs.conan.io/en/latest/creating_packages/getting_started.html#the-test-package-folder
#include <boost/simd/pack.hpp>
#include <boost/date_time.hpp>
#include <iostream>

namespace bs = boost::simd;

int main()
{
    using namespace boost::date_time;
    bs::pack<float,4> p{1.f,2.f,3.f,4.f};
    std::cout << "Boost.SIMD test from README.md : " << p + 10*p << "\n";
    std::cout << "Boost.date_time interop test: " << boost::gregorian::date(2021, Aug, 4) << "\n";
    return 0;
}
