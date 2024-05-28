#include <iostream>
#include "lodepng.h"

int main(int argc, const char *argv[])
{
    LodePNGCompressSettings compress_settings;
    lodepng_compress_settings_init(&compress_settings);

    printf("compress_settings.btype = %d\n", compress_settings.btype);

    return 0;
}
