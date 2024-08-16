#include <cstdlib>
#include <iostream>

#include <folly/Format.h>
#include <folly/FBString.h>


int main() {
    folly::fbstring message{"The answer is {}."};
    std::cout << folly::format(message, 42);
    return EXIT_SUCCESS;
}
