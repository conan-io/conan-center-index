#include "libyuv.h"

int main() {
    uint8_t in[16] = {};
    uint8_t out[16] = {};
    libyuv::ConvertToARGB(in, 16, out, 0, 0, 0, 1, 1, 0, 0,
                          libyuv::RotationMode::kRotate0, 0);
    return 0;
}
