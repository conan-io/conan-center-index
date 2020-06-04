#include "qrcodegen/QrCode.hpp"

int main() {
    qrcodegen::QrCode::encodeText("test", qrcodegen::QrCode::Ecc::MEDIUM)
            .toSvgString(0);

    return 0;
}
