#include "hwy/aligned_allocator.h"
#include "hwy/highway.h"

#include <iostream>

HWY_BEFORE_NAMESPACE();
namespace {
namespace HWY_NAMESPACE {

void test()
{
    const HWY_FULL(uint32_t) d;

    const size_t count = 5 * Lanes(d);
    auto x_array = hwy::AllocateAligned<uint32_t>(count);

    uint32_t result = 0;
    uint32_t expected = 0;

    for (size_t i = 0; i < count; ++i) {
        x_array[i] = i;
        expected += x_array[i];
    }

    for (size_t i = 0; i < count; i += Lanes(d)) {
        const auto x = Load(d, &x_array[i]);
#if HWY_MAJOR == 0 && HWY_MINOR < 14
        result += GetLane(SumOfLanes(x));
#else
        result += GetLane(SumOfLanes(d, x));
#endif
    }

    std::cout << "result = " << result << ", expected = " << expected << '\n';
}

} // namespace HWY_NAMESPACE
} // namespace
HWY_AFTER_NAMESPACE();

int main()
{
    HWY_NAMESPACE::test();
    return 0;
}
