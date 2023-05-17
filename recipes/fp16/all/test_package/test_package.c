#include <fp16.h>

#include <stdint.h>

int main() {
    uint16_t a = fp16_ieee_from_fp32_value(35.f);
    return 0;
}
