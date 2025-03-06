#include <stdint.h>
#include "jtckdint.h"

int main(void) {
    uint32_t c;
    int32_t a = 0x7fffffff;
    int32_t b = 2;
    ckd_add(&c, a, b);

    return 0;
}
