#include <cstdlib>
#include <iostream>

#include "lefticus/tools/non_promoting_ints.hpp"

using namespace lefticus::tools::literals;

int main() {
    const auto npint1 = std::int8_t{ 2 } + 1_np8;
    if (std::is_same_v<decltype(npint1), const lefticus::tools::int_np<std::int8_t>>) {
        std::cout << "npint1 is a non-promoting int" << std::endl;
    }

    return EXIT_SUCCESS;
}
