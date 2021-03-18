#include <pffft.h>
#include <stdio.h>

int main() {

    int s = pffft_simd_size();
    printf(s);
    return 0;
}
