#include <libnova/libnova.h>

#include <stdio.h>

int main(void) {
    double julian_day = ln_get_julian_from_sys();
    printf("JD %f\n", julian_day);

    struct ln_helio_posn pos;
    ln_get_mars_helio_coords(julian_day, &pos);
    printf("Mars L %f B %f R %f\n", pos.L, pos.B, pos.R);

    return 0;
}
