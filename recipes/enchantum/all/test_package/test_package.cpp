#include <cstdlib>
#include <iostream>
#include <enchantum/enchantum.hpp>

enum class Color : int { Red, Green };

int main() {
    const auto name = enchantum::to_string(Color::Red);
    std::cout << "enchantum::to_string(Color::Red) length: " << name.size() << std::endl;
    return name.empty() ? EXIT_FAILURE : EXIT_SUCCESS;
}
