#include <iostream>
#include <vector>
#include <cstdint>
#include <fstream>

#include "lodepng.h"

int main()
{
    std::ifstream stream("bees.png", std::ios::in | std::ios::binary);
    std::vector<uint8_t> data((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());

    std::vector<uint8_t> decoded;
    unsigned width = 0, height = 0;
    lodepng::decode(decoded, width, height, data);
    stream.close();

    return 0;
}
