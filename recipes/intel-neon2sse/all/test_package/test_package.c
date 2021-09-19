#include <NEON_2_SSE.h>
#include <stdio.h>

int main()
{
    uint64_t a = 0x0102030405060708;
    uint64_t b = 0x0102030405060708;
    union {
        char c[8];
        uint64_t i;
    } c;
    uint8x8_t va = vcreate_u8(a);
    uint8x8_t vb = vcreate_u8(b);
    uint8x8_t vc = vmul_u8(va, vb);

    vst1_u8(c.c, vc);

    if (c.i != 0x0104091019243140) {
        fprintf(stderr, "Wrong result\n");
        return 1;
    } else {
        printf("test_package ran successfully\n");
    }

    return 0;
}
