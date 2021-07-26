#include <pffft.h>
#include <stdio.h>

int main() {

    int s = pffft_simd_size();
    printf("%d\n",s);
    return 0;
}
