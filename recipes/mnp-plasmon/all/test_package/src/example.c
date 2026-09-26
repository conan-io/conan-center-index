#include "mnp_plasmon.h"
#include <stdio.h>

int main(void)
{
    sphere_response_t r = mnp_simulate_sphere_response("Au", 550.0, 25.0, 1.0);
    printf("c_ext = %.4f\n", r.c_ext);
    printf("c_sca = %.4f\n", r.c_sca);
    printf("c_abs = %.4f\n", r.c_abs);
    return 0;
}
