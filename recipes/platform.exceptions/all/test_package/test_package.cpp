#include <Platform.Exceptions.h>

#include <iostream>

using namespace Platform::Exceptions;

auto main() -> int {
    try {
        Ensure::Always::ArgumentNotNull(nullptr);
    } catch (std::exception& e) {
        std::cout << e.what() << std::endl;
    }
}
