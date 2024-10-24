#include <vector>
#include <iostream>

#include "tl/enumerate.hpp"

int main() {
    std::vector<int> data = {1, 2, 3, 4, 5};

    for (auto&& [index, element] : data | tl::views::enumerate) {
        std::cout << index << " " << element << '\n';
    }
}
