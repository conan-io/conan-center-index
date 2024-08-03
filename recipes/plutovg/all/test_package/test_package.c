#include <plutovg/plutovg.h>

int main(void)
{
    const int width = 150;
    const int height = 150;

    plutovg_surface_t* surface = plutovg_surface_create(width, height);
    plutovg_canvas_t* canvas = plutovg_canvas_create(surface);

    float center_x = width * 0.5;
    float center_y = height * 0.5;
    float face_radius = 70;
    float eye_radius = 10;
    float mouth_radius = 50;
    float eye_offset_x = 25;
    float eye_offset_y = 20;
    float eye_x = center_x - eye_offset_x;
    float eye_y = center_y - eye_offset_y;

    const float pi = 3.14159265358979323846;

    plutovg_surface_destroy(surface);
    plutovg_canvas_destroy(canvas);
    return 0;
}
