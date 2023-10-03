// Workaround for missing includes in platform.equality
#include <concepts>
#include <ranges>
#include <string>
#include <unordered_map>
#include <utility>

#include <Platform.Equality.h>

#include <any>
#include <iostream>

auto main() -> int {
    boolalpha(std::cout);

    #define eval(expr) #expr << ": " << (expr)

    using std::any;
    std::cout << eval(any(5) == any(5)) << std::endl;
    std::cout << eval(any(5) == any(5u)) << std::endl;

    #undef eval
}
