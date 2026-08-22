#include <cstdlib>
#include <iostream>

#include "zpp_throwing.h"

zpp::throwing<int> foo(bool success) {
    if (!success) {
        // Throws an exception.
        co_yield std::runtime_error("My runtime error");
    }

    // Returns a value.
    co_return 1337;
}

int main() {
    return zpp::try_catch([]() -> zpp::throwing<int> {
        std::cout << "Hello World\n";
        std::cout << co_await foo(false) << '\n';;
        co_return 0;
    }, [&](const std::exception & error) {
        std::cout << "std exception caught: " << error.what() << '\n';
        return 0;
    }, [&]() {
        std::cout << "Unknown exception\n";
        return 0;
    });
}
