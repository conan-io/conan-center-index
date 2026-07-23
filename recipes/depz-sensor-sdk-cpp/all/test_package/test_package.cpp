#include <depz/crc.hpp>

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>

int main() {
    std::array<std::byte, 4> data{
        std::byte{0x01}, std::byte{0x02}, std::byte{0x03}, std::byte{0x04}};
    std::uint8_t crc = depz::crc8_maxim(data);
    std::printf("depz::crc8_maxim -> 0x%02X\n", static_cast<unsigned>(crc));
    return 0;
}
