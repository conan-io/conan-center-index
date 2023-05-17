#include <cstdlib>
#include <vector>
#include "fmt/ranges.h"

int main() {
    std::vector<char> numbers;
    fmt::format_to(std::back_inserter(numbers), "{}{}{}", 1, 2, 3);
    const std::string str_numbers = fmt::format("{}", numbers);
    fmt::print("numbers: {}\n", str_numbers);
    return EXIT_SUCCESS;
}
