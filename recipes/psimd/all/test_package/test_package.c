#include <psimd.h>

#include <stdint.h>

int main() {
#if defined(__GNUC__) || defined(__clang__)
    psimd_u32 a = psimd_splat_u32(UINT32_C(0x80000000));
#endif
    return 0;
}
