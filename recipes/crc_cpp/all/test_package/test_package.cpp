#include <cstdint>
#include <vector>
#include <iostream>

#include "crc_cpp.h"

using namespace crc_cpp;

[[nodiscard]] auto compute_crc32(std::vector<std::uint8_t> const &message)
{
    crc_cpp::crc32 crc;

    for(auto c : message) {
        crc.update(c);
    }

    return crc.final();
}


int main()
{
    std::cout << "Smoke Testing crc_cpp with CRC32\n";

    std::vector<std::uint8_t> const message{'1', '2', '3', '4', '5', '6', '7', '8', '9'};

    auto const result = compute_crc32(message);
    if(result == 0xCBF43926) {
        std::cout << "Success!\n";
        return 0;
    } else {
        std::cout << "Failed!??\n";
        return -1;
    }
}
