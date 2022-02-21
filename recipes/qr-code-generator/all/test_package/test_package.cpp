#if QR_USE_OLD_INCLUDE
#include "qrcodegen/QrCode.hpp"
#else
#include "qrcodegen/qrcodegen.hpp"
#endif

#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

namespace {
    // Returns a string of SVG code for an image depicting the given QR Code, with the given number
    // of border modules. The string always uses Unix newlines (\n), regardless of the platform.
    std::string toSvgString(const qrcodegen::QrCode &qr, int border) {
        if (border < 0)
            throw std::domain_error("Border must be non-negative");
        if (border > std::numeric_limits<int>::max() / 2 || border * 2 > std::numeric_limits<int>::max() - qr.getSize())
            throw std::overflow_error("Border too large");

        std::ostringstream sb;
        sb << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
        sb << "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n";
        sb << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" viewBox=\"0 0 ";
        sb << (qr.getSize() + border * 2) << " " << (qr.getSize() + border * 2) << "\" stroke=\"none\">\n";
        sb << "\t<rect width=\"100%\" height=\"100%\" fill=\"#FFFFFF\"/>\n";
        sb << "\t<path d=\"";
        for (int y = 0; y < qr.getSize(); y++) {
            for (int x = 0; x < qr.getSize(); x++) {
                if (qr.getModule(x, y)) {
                    if (x != 0 || y != 0)
                        sb << " ";
                    sb << "M" << (x + border) << "," << (y + border) << "h1v1h-1z";
                }
            }
        }
        sb << "\" fill=\"#000000\"/>\n";
        sb << "</svg>\n";
        return sb.str();
    }
}

int main() {
    std::cout << toSvgString(qrcodegen::QrCode::encodeText("test", qrcodegen::QrCode::Ecc::MEDIUM), 0);
    return 0;
}
