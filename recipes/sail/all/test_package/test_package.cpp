#include <iostream>

#include <sail-c++/sail-c++.h>

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;

    const sail::image image(SAIL_DEMO_FILE_PATH);

    if (!image.is_valid()) {
        return 1;
    }

    std::cout
        << "Size: "
        << image.width() << 'x' << image.height()
        << ", bytes per line: "
        << image.bytes_per_line()
        << ", pixel format: "
        << sail::image::pixel_format_to_string(image.pixel_format())
        << ", pixels: "
        << image.pixels()
        << std::endl;

    return 0;
}
