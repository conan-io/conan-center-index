#include "hwy/highway.h"

#include <iostream>

HWY_BEFORE_NAMESPACE();
namespace HWY_NAMESPACE {

void test()
{
    const HWY_FULL(float) d;
    const auto a = Iota(d, 2);
    const auto b = Iota(d, 3);
    
    std::cout << "(0 + 1) + (0 + 1 + 2) = "
    	<< GetLane(SumOfLanes(a + b)) << '\n';
}

} // namespace HWY_NAMESPACE
HWY_AFTER_NAMESPACE();

int main()
{
	HWY_NAMESPACE::test();
    return 0;
}
