#include "ZXing/BarcodeFormat.h"
#include "ZXing/MultiFormatWriter.h"
#include "ZXing/BitMatrix.h"
#include "ZXing/ByteMatrix.h"
#include "ZXing/TextUtfEncoding.h"

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <cstdlib>
#include <iostream>

using namespace ZXing;

int main()
{
    auto format = BarcodeFormat::QR_CODE;
    int width = 100, height = 100;
    int margin = 10;
    int eccLevel = 8;
    std::string text = "Hello conan world!";
    std::string outPath = "output.png";

    try {
        MultiFormatWriter writer(format);
        writer.setMargin(margin);
        writer.setEccLevel(eccLevel);
        auto bitmap = writer.encode(TextUtfEncoding::FromUtf8(text), width, height).toByteMatrix();
        int success = stbi_write_png(outPath.c_str(), bitmap.width(), bitmap.height(), 1, bitmap.data(), 0);
        if (!success) {
            std::cerr << "Failed to write image: " << outPath << '\n';
            return EXIT_FAILURE;
        }
    } catch (const std::exception &e) {
        std::cerr << "An error occured:\n" << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
