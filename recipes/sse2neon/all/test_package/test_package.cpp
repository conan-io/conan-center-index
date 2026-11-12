#include <stdio.h>
#include "sse2neon.h"

int main(void) {
    __m128i a = _mm_set_epi32(4, 3, 2, 1);
    __m128i b = _mm_set_epi32(40, 30, 20, 10);

    __m128i sum = _mm_add_epi32(a, b);

    int32_t result[4];
    _mm_storeu_si128((__m128i *)result, sum);

    printf("Result: %d %d %d %d\n", result[0], result[1], result[2], result[3]);

    return 0;
}
