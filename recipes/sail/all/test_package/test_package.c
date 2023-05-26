#include <stdio.h>

#include <sail/sail.h>

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;

    struct sail_image *image;
                  
    SAIL_TRY_OR_EXECUTE(sail_load_from_file(SAIL_DEMO_FILE_PATH, &image),
        /* on error */ return 1);

    printf("Size: %ux%u, bytes per line: %u, "
           "pixel format: %s, pixels: %p\n",
             image->width,
             image->height,
             image->bytes_per_line,
             sail_pixel_format_to_string(image->pixel_format),
             image->pixels);

    sail_destroy_image(image);

    return 0;
}
