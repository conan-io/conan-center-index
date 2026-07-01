#include <iostream>
#include <neko/function/utilities.hpp>


int main(void) {
    using namespace neko::ops::pipe;

    // Chaining operations
    auto toUpper = [](std::string s) { return neko::util::string::toUpper<std::string>(s); };

    auto result = "hello" | neko::util::plusDoubleQuote | toUpper; // result = "HELLO"
    std::cout << "result" << " = " << result << std::endl;

    return EXIT_SUCCESS;
}