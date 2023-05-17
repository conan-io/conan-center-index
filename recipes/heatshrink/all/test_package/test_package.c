#include "heatshrink_encoder.h"

int main() {
#if HEATSHRINK_DYNAMIC_ALLOC
    heatshrink_encoder *hse = heatshrink_encoder_alloc(8, 7);
    heatshrink_encoder_reset(hse);
    heatshrink_encoder_free(hse);
#else
    heatshrink_encoder hse;
    heatshrink_encoder_reset(&hse);
#endif

    return 0;
}
