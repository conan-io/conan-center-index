#include <lqr.h>

#include <stdlib.h>

int main() {
    gint channels = 3;
    gint w = 100;
    gint h = 100;
    guchar *rgb_buffer = (guchar *) malloc(channels * w * h * sizeof(guchar));

    LqrCarver *r = lqr_carver_new(rgb_buffer, w, h, channels);
    lqr_carver_destroy(r);

    return 0;
}
