#include "stdio.h"

#define SDF_IMPLEMENTATION
#include "sdf.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

int main(int argc, char **argv)
{
    int width, height, bpp;
    unsigned char* img_data = stbi_load("not a valid/path/fake_img.png", &width, &height, &bpp, 0);
    if (img_data == NULL)
    {
        printf("Test\n"); // This should be printed always
    }
    return 0;
}
