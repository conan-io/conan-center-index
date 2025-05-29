#include <vector>
#include <cstdint>
#include "qoixx.hpp"

int main(void) {
    constexpr qoixx::qoi::desc desc{
    .width = 8,
    .height = 4,
    .channels = 3,
    .colorspace = qoixx::qoi::colorspace::srgb,
    };

    const std::vector<std::uint8_t> original = {
        130,   0, 212, 124, 204,  88,  79,  26, 210, 104, 117,   4, 137, 191,  80, 204,
         65, 175,  38, 160, 207, 182, 174,  59,  83,  18, 227,   4, 234, 150,  97, 131,
         62,  95, 167, 236, 132, 143,  78, 175,  86, 172, 237, 113, 195,  87, 227, 242,
         13, 189, 125,  33,  16,  79, 165, 247, 216, 193, 192, 113, 254, 176, 172, 227,
         94, 105, 146, 232, 150,  39, 148, 238, 105,  65,  23,   4,  33, 252, 243, 111,
        120,  32, 150, 144,  96,  66,   9, 102, 226, 245, 145, 153, 240, 183,  60, 132
    };

    const auto encoded = qoixx::qoi::encode<std::vector<std::uint8_t>>(original, desc);
    const auto [decoded, decoded_desc] = qoixx::qoi::decode<std::vector<std::uint8_t>>(encoded);
    return 0;
}
