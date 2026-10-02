#include <cstdlib>
#include <iterator>
#include <string>
#include <vector>

#ifdef FMT_TEST_USE_MODULE
import fmt;
#else
#include "fmt/ranges.h"
#endif

int main() {
    std::vector<char> numbers;
    fmt::format_to(std::back_inserter(numbers), "{}{}{}", 1, 2, 3);
    const std::string str_numbers = fmt::format("{}", numbers);
    fmt::print("numbers: {}\n", str_numbers);
    return EXIT_SUCCESS;
}
