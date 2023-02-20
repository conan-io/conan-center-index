#include <cstdlib>
#include "gli/gli.hpp"

int main (int argc, char * argv[]) {
    auto texture = gli::texture1d(gli::FORMAT_RGBA8_UNORM_PACK8, gli::extent1d(10), 1);

    for (int i = 0; i < 10; i++)
    {
        texture.store(gli::extent1d(i), 0, glm::u8vec4(i * 255 / 9));
    }

    gli::save(texture, "test.dds");

    return EXIT_SUCCESS;
}
