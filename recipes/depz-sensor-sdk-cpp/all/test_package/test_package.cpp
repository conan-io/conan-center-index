#include <depz/crc.hpp>
#include <depz/device.hpp>

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>

int main() {
    std::array<std::byte, 4> data{
        std::byte{0x01}, std::byte{0x02}, std::byte{0x03}, std::byte{0x04}};
    std::uint8_t crc = depz::crc8_maxim(data);
    std::printf("depz::crc8_maxim -> 0x%02X\n", static_cast<unsigned>(crc));

    // Links the live-device layer (over depz-sensor-sdk-c): a missing port throws.
    try {
        depz::Device::open("depz-test-package-no-such-port");
        return 1;
    } catch (const depz::Error& e) {
        std::printf("depz::Device::open(no such port) -> %s\n", e.what());
    }
    return 0;
}
