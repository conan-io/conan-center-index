#include <fxdiv.h>

#include <stddef.h>
#include <stdint.h>

void divide_array_fxdiv(size_t length, uint32_t array[], uint32_t divisor) {
    const struct fxdiv_divisor_uint32_t precomputed_divisor = fxdiv_init_uint32_t(divisor);
    for (size_t i = 0; i < length; ++i) {
        array[i] = fxdiv_quotient_uint32_t(array[i], precomputed_divisor);
    }
}

int main() {
    uint32_t arr[] = {19, 3219, 34, 4, 365};
    divide_array_fxdiv(5, arr, 7);
    return 0;
}
