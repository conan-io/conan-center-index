#include <iostream>
#include "cthash/cthash.hpp"

using namespace cthash::literals;

int main(void) {
    constexpr auto my_hash = cthash::sha3_256{}.update("hello there!").final();

    std::cout << my_hash << std::endl;

    return 0;
}
