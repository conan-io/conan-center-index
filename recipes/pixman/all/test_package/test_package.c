#include <pixman.h>
#include <pixman-version.h>

#include <stdio.h>
#include <stdlib.h>

#define SIZE 128
#define GRADIENTS_PER_ROW 7
#define NUM_ROWS ((NUM_GRADIENTS + GRADIENTS_PER_ROW - 1) / GRADIENTS_PER_ROW)
#define WIDTH (SIZE * GRADIENTS_PER_ROW)
#define HEIGHT (SIZE * NUM_ROWS)
#define NUM_GRADIENTS 35

#define double_to_color(x)                  \
    (((uint32_t) ((x)*65536)) - (((uint32_t) ((x)*65536)) >> 16))

#define PIXMAN_STOP(offset,r,g,b,a)         \
    { pixman_double_to_fixed (offset),      \
        {                                   \
            double_to_color (r),            \
            double_to_color (g),            \
            double_to_color (b),            \
            double_to_color (a)             \
        }                                   \
    }


static const pixman_gradient_stop_t stops[] = {
    PIXMAN_STOP (0.25,       1, 0, 0, 0.7),
    PIXMAN_STOP (0.5,        1, 1, 0, 0.7),
    PIXMAN_STOP (0.75,       0, 1, 0, 0.7),
    PIXMAN_STOP (1.0,        0, 0, 1, 0.7)
};

#define NUM_STOPS (sizeof (stops) / sizeof (stops[0]))

int main() {
    pixman_point_fixed_t c;
    double angle;
    pixman_image_t *src_img;

    printf("pixman version: %s\n", PIXMAN_VERSION_STRING);

    c.x = pixman_double_to_fixed (0);
    c.y = pixman_double_to_fixed (0);

    angle = (0.5 / NUM_GRADIENTS + 1 / (double)NUM_GRADIENTS) * 720 - 180;
    src_img = pixman_image_create_conical_gradient (&c, pixman_double_to_fixed(angle), stops, NUM_STOPS);
    pixman_image_unref (src_img);

    return EXIT_SUCCESS;
}
