#include <libnova/libnova.h>

#include <stdio.h>

int main(void) {
    struct ln_date date;
    date.years = 1987;
    date.months = 4;
    date.days = 10;
    date.hours = 19;
    date.minutes = 21;
    date.seconds = 0.0;
    double julian_day = ln_get_julian_day(&date);
    printf("JD %f\n", julian_day);

    struct ln_helio_posn pos;
    ln_get_mars_helio_coords(julian_day, &pos);
    printf("Mars L %f B %f R %f\n", pos.L, pos.B, pos.R);

    return 0;
}
