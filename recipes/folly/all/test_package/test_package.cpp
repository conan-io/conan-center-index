#include <cstdlib>
#include <iostream>
#include <folly/Format.h>

int main()
{
    auto str = folly::format("The answers are {} and {}", 23, 42);
    std::cout << str << std::endl;
    return EXIT_SUCCESS;
}
