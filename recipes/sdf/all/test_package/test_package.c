#include "stdio.h"

#define SDF_IMPLEMENTATION
#include "sdf.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return 1;
    }

    int width, height, bpp;
    unsigned char* img_data = stbi_load(argv[1], &width, &height, &bpp, 0);
    if(img_data == NULL)
    {
        fprintf(stderr, "Could not load image: %s\n", stbi_failure_reason());
        return 1;
    }

    unsigned char* dest_data = malloc(width * height * bpp);
    if(dest_data == NULL)
    {
        stbi_image_free(img_data);
        return 1;
    }

    sdfBuildDistanceField(dest_data, width, 2.0f, img_data, width, height, width);

    free(dest_data);
    stbi_image_free(img_data);

    return 0;
}
