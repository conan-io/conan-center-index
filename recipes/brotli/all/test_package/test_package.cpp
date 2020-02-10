#include <brotli/encode.h>
#include <brotli/decode.h>

#include <cstdlib>
#include <cstring>
#include <string>
#include <iostream>

int main() {
    std::string input = "some long text that we would like to compress if possible....";
    uint8_t buffer[128];
    size_t outputsize = sizeof(buffer);
    BROTLI_BOOL result = BrotliEncoderCompress(
        BROTLI_DEFAULT_QUALITY,
        BROTLI_DEFAULT_WINDOW,
        BROTLI_DEFAULT_MODE,
        input.size(),
        reinterpret_cast<const uint8_t*>(input.c_str()),
        &outputsize,
        buffer);
    if (result != BROTLI_TRUE) {
        std::cout << "BrotliEncoderCompress failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "string went from " << input.size() << " bytes to " << outputsize << " bytes.\n";

    char buffer2[128];
    size_t reconstructedSize = sizeof(buffer2);
    result = BrotliDecoderDecompress(
        outputsize,
        buffer,
        &reconstructedSize,
        reinterpret_cast<uint8_t*>(buffer2));
    if (result != BROTLI_TRUE) {
        std::cout << "BrotliDecoderDecompress failed\n";
        return EXIT_FAILURE;
    }
    if (reconstructedSize != input.size()) {
        std::cout << "Size of input (" << input.size() << ") and output (" << reconstructedSize << ") do not match\n";
        return EXIT_FAILURE;
    }
    if (strncmp(input.c_str(), buffer2, input.size())) {
        std::cout << "The original string could not be reconstructed\n";
        return EXIT_FAILURE;
    }
    std::cout << "String was correctly reconstructed\n";
    std::cout << "Input:  \"" << input << "\"\n";
    std::cout << "Output: \"" << buffer2 << "\"\n";

    return EXIT_SUCCESS;
}
