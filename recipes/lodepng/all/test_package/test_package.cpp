#include <iostream>
#include <vector>
#include <cstdint>
#include <fstream>

#include "lodepng.h"

int main(int argc, const char *argv[])
{
    if (argc < 2) {
        std::cerr << "Need at least one argument\n";
    }
    std::ifstream stream(argv[1], std::ios::in | std::ios::binary);
    std::vector<uint8_t> data((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());

    std::cout << "file name " << argv[1] << "\n";
    std::cout << "file size " << data.size() << " bytes\n";

    std::vector<uint8_t> decoded;
    unsigned width = 0, height = 0;
    unsigned error = lodepng::decode(decoded, width, height, data);
    if (error != 0) {
        std::cerr << "lodepng::decode returned with error code " << error << "\n";
        return 1;
    }
    std::cout << "image size: " << width << " x " << height << " pixels.\n";

    stream.close();

    return 0;
}
