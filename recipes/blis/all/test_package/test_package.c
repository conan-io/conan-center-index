#include <blis.h>

int main()
{
    obj_t a1;
    num_t dt;
    dim_t m, n;
    inc_t rs, cs;

    dt = BLIS_DOUBLE; m  = 4; n  = 3;
                      rs = 1; cs = 4;
    bli_obj_create( dt, m, n, rs, cs, &a1 );
    bli_obj_free( &a1 );
}
