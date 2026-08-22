#include "ZXing/BarcodeFormat.h"
#include "ZXing/BitMatrix.h"
#include "ZXing/BitMatrixIO.h"
#include "ZXing/CharacterSet.h"
#include "ZXing/MultiFormatWriter.h"
#include "ZXing/TextUtfEncoding.h"

#include <algorithm>
#include <cctype>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include <stb_image_write.h>

using namespace ZXing;

int main(int argc, char* argv[])
{
    int width = 100, height = 100;
    int margin = 10;
    int eccLevel = 8;
    auto encoding = CharacterSet::Unknown;
    auto format = BarcodeFormat::QRCode;
    std::string text = "Hello conan world!";
    std::string outPath = "output.png";

    try {
        auto writer = MultiFormatWriter(format).setMargin(margin).setEncoding(encoding).setEccLevel(eccLevel);
        auto matrix = writer.encode(TextUtfEncoding::FromUtf8(text), width, height);
        auto bitmap = ToMatrix<uint8_t>(matrix);

        int success = stbi_write_png(outPath.c_str(), bitmap.width(), bitmap.height(), 1, bitmap.data(), 0);
        if (!success) {
            std::cerr << "Failed to write image: " << outPath << std::endl;
            return -1;
        }
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return -1;
    }

    return 0;
}
