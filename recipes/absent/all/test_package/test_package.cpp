#include <iostream>
#include <optional>
#include <absent/absent.h>

using namespace rvarago::absent;

int main() {
    constexpr auto maybe_an_approximated_answer = std::optional{41};
    constexpr auto exact_answer = (maybe_an_approximated_answer | [](auto v) { return v + 1; }).value();
    static_assert(exact_answer == 42);
    std::cout << "rvarago::absent works! The exact answer is: " << exact_answer << '\n';
    return 0;
}
