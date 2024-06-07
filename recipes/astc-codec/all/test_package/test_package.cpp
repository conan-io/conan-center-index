#include <iostream>
#include <vector>
#include <cstdint>
#include <fstream>
#include <string>

#include <astc-codec/astc-codec.h>

int main(int argc, char **argv)
{
    std::ifstream stream("fake-file.astc", std::ios::in | std::ios::binary);
    std::vector<uint8_t> astc_data((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());

    bool success = astc_codec::ASTCDecompressToRGBA(
    astc_data.data(), 100, 100, 100, astc_codec::FootprintType::k4x4, NULL, 100, 100);

    std::cout << "Test: " << success << std::endl;

    stream.close();

	return 0;
}
