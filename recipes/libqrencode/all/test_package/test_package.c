#include <qrencode.h>

int main()
{
    QRcode *code = QRcode_encodeString("conan-center", 0, QR_ECLEVEL_L, QR_MODE_8, 1);
    return 0;
}
