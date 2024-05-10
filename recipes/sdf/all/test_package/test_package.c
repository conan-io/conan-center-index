#include "stdio.h"

#define SDF_IMPLEMENTATION
#include "sdf.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

int main(int argc, char **argv)
{

    int width, height, bpp;
    unsigned char* dest_data = malloc(width * height * bpp);
    unsigned char* img_data = stbi_load("not a valid/path/fake_img.png", &width, &height, &bpp, 0);
    if (img_data == NULL)
    {
        printf("Test\n"); // This should be printed always
    }

    int result = sdfBuildDistanceField(dest_data, width, 2.0f, img_data, width, height, width);
    printf("Result: %d\n", result);

    free(dest_data);
    stbi_image_free(img_data);

    return 0;
}
