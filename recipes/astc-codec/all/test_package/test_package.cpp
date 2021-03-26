#include <iostream>
#include <vector>
#include <cstdint>
#include <fstream>
#include <string>

#include <astc-codec/astc-codec.h>

int main(int argc, char **argv)
{
    if (argc < 4) {
        std::cerr << "Need at least three argument\n";
    }
    std::ifstream stream(argv[1], std::ios::in | std::ios::binary);
    std::vector<uint8_t> astc_data((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());

    const size_t width = std::stoi(argv[2]);
    const size_t height = std::stoi(argv[3]);

    std::vector<uint8_t> result;
    result.resize(width * height * 4);

    bool success = astc_codec::ASTCDecompressToRGBA(
        astc_data.data(), astc_data.size(), width, height, astc_codec::FootprintType::k4x4,
        result.data(), result.size(), /* stride */ width * 4);

    stream.close();

	return 0;
}
