#include <png++/png.hpp>

int main() {
    png::image<png::rgb_pixel> image(128, 128);
    for (png::uint_32 y = 0; y < image.get_height(); ++y) {
        for (png::uint_32 x = 0; x < image.get_width(); ++x) {
            image[y][x] = png::rgb_pixel(x, y, x + y);
        }
    }
    image.write("rgb.png");
    return 0;
}
