#include <stdint.h>
#include <simde/x86/sse4.2.h>

int main(void) {
    simde__m128i a = simde_mm_set_epi8(
        INT8_C(-105), INT8_C(-116), INT8_C( -45), INT8_C(-102),
        INT8_C(  -3), INT8_C(  92), INT8_C( -99), INT8_C( 100),
        INT8_C(  30), INT8_C(-115), INT8_C(  82), INT8_C(  84),
        INT8_C(-106), INT8_C(  66), INT8_C(-107), INT8_C( 116)
    );
    int la = 0;
    simde__m128i b = simde_mm_set_epi8(
        INT8_C( -89), INT8_C(  65), INT8_C(  68), INT8_C( -29),
        INT8_C(-101), INT8_C( 113), INT8_C( -11), INT8_C(  53),
        INT8_C(  -5), INT8_C( -76), INT8_C(  28), INT8_C(-120),
        INT8_C(  64), INT8_C(  43), INT8_C(-127), INT8_C( -44)
    );
    int lb = 2;
    int r = simde_mm_cmpestrs(a, la, b, lb, 0);

    if (r != 1) {
        return 1;
    }

    return 0;
}
