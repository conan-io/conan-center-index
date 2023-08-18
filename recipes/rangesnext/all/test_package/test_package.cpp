#include <cor3ntin/rangesnext/enumerate.hpp>

#include <iostream>

namespace rangesnext = cor3ntin::rangesnext;

template <class RangeT>
bool test_enumerate_with(RangeT &&range) {
    auto enumerated_range = rangesnext::enumerate(range);

    std::size_t idx_ref = 0;
    auto it_ref = std::ranges::begin(range);

    bool success = true;
    for (auto &&[i, v] : enumerated_range) {
        std::cout << i << " - " << v << "\n";

        success = (i == idx_ref++) && (v == *it_ref++);
        if (success == false) {
            return false;
        }
    }

    return true;
}

int main() {
    int const test_array[] = {9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    test_enumerate_with(test_array);
}
