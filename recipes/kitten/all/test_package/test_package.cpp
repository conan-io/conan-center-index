#include "kitten/instances/optional.h"
#include "kitten/kitten.h"

#include <iostream>
#include <optional>

using namespace rvarago::kitten;

int main() {
    auto constexpr maybe_an_approximate_answer = std::optional{41};
    auto constexpr exact_answer =
        (maybe_an_approximate_answer | [](auto const& el) { return el + 1; }).value();
    static_assert(42 == exact_answer);
    std::cout << "rvarago::kitten works! The exact answer is: " << exact_answer << '\n';
    return 0;
}
