#include <ftms/ftms.h>
int main() {
    const uint8_t bytes[8] = {1, 0, 0, 0, 2, 0, 0, 0};
    ftms_features value;
    return ftms_decode_features(bytes, sizeof(bytes), &value) != FTMS_OK || value.machine != 1 || value.target != 2;
}
