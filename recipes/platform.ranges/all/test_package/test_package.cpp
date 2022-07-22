#include <Platform.Ranges.h>

using namespace Platform::Ranges;

int main() {
    auto range1 = Range(1, 3);
    auto range2 = Range(5);
    range1.Contains(1);
    range1.Contains({2, 3});
    range1.Contains({3, 4});
    Platform::Ranges::Difference(range1);
    auto isEqual = range1 == range2;
    return 0;
}
