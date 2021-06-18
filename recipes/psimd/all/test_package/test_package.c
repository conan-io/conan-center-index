#include <psimd.h>

#include <stdint.h>

int main() {
    psimd_u32 a = psimd_splat_u32(UINT32_C(0x80000000));
    return 0;
}
