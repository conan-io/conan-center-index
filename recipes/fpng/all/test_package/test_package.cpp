#include <vector>
#include <cstdint>

#include "fpng.h"

int main() {
	fpng::fpng_init();

    auto const WIDTH = 800;
    auto const HEIGHT = 600;
    auto const CHANNEL = 3;

    auto buffer = std::vector<uint8_t>{};
    buffer.reserve(WIDTH * HEIGHT * CHANNEL);

    uint32_t flags = 0;

    auto image = std::vector<uint8_t>{};
    fpng::fpng_encode_image_to_memory(buffer.data(), WIDTH, HEIGHT, CHANNEL, image, flags);

    return 0;
}
