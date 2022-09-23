#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "png.h"


int main(void) {
    png_structp png_ptr;
    png_infop info_ptr;

    fprintf(stderr, "   Compiled with libpng %s; using libpng %s.\n", PNG_LIBPNG_VER_STRING, png_libpng_ver);
    png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    info_ptr = png_create_info_struct(png_ptr);

    return EXIT_SUCCESS;
}
