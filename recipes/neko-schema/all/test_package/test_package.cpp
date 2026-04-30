#include <neko/schema/types.hpp>
#include <iostream>
#include <string>

int main() {
    neko::int32 value = 42;
    neko::uint64 large = 9999999999ULL;
    neko::int8 tiny = 127;

    std::cout << "int32 value: " << value << "\n";
    std::cout << "uint64 value: " << large << "\n";
    std::cout << "int8 value: " << static_cast<int>(tiny) << "\n";

    neko::cstr greeting = "Hello from Conan!";
    std::string text = "Testing neko types";

    std::cout << "cstr: " << greeting << "\n";
    std::cout << "string: " << text << "\n";

    auto state = neko::State::Completed;
    auto priority = neko::Priority::Normal;
    std::cout << "State: " << neko::toString(state) << "\n";
    std::cout << "Priority: " << neko::toString(priority) << "\n";

    static_assert(std::is_same_v<neko::int32, std::int32_t>);
    static_assert(std::is_same_v<neko::uint64, std::uint64_t>);
    static_assert(std::is_same_v<neko::int8, std::int8_t>);

    std::cout << "Conan package test passed!\n";
    return 0;
}
