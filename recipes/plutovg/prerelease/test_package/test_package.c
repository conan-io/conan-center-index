#include "plutovg.h"

int main(void)  {
    const int width = 150;
    const int height = 150;

    plutovg_surface_t* surface = plutovg_surface_create(width, height);
    plutovg_t* pluto = plutovg_create(surface);

    plutovg_surface_destroy(surface);
    plutovg_destroy(pluto);

    return 0;
}
