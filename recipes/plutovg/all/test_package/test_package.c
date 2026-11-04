#include <plutovg/plutovg.h>

int main(void) {
    const int width = 150;
    const int height = 150;

    plutovg_surface_t* surface = plutovg_surface_create(width, height);
    plutovg_canvas_t* canvas = plutovg_canvas_create(surface);

    plutovg_surface_destroy(surface);
    plutovg_canvas_destroy(canvas);

    return 0;
}
