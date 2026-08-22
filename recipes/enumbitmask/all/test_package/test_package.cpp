#include <iostream>

#include "EnumBitmask.hpp"

enum class OpenMode {
    Append = 1,
    Binary = 2,
    Input = 4,
    Output = 8,
};
DEFINE_BITMASK_OPERATORS(OpenMode)


int main() {
    constexpr auto mode = OpenMode::Binary | OpenMode::Input;

    constexpr auto flag = mode & OpenMode::Binary;

    return 0;
}
