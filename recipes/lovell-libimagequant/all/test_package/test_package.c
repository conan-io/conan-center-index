#include <stdio.h>
#include <stdlib.h>
#include <libimagequant.h>

int main(void) {
    enum { W = 4, H = 4 };
    liq_attr *attr = liq_attr_create();
    if (!attr) return EXIT_FAILURE;

    liq_color pixels[W * H];
    for (int i = 0; i < W * H; i++) {
        pixels[i].r = (unsigned char)(i * 16);
        pixels[i].g = (unsigned char)(255 - i * 16);
        pixels[i].b = 0;
        pixels[i].a = 255;
    }

    liq_image *image = liq_image_create_rgba(attr, pixels, W, H, 0);
    liq_result *result = NULL;
    if (!image || liq_image_quantize(image, attr, &result) != LIQ_OK) return EXIT_FAILURE;

    printf("libimagequant palette colors: %u\n", liq_get_palette(result)->count);

    liq_result_destroy(result);
    liq_image_destroy(image);
    liq_attr_destroy(attr);
    return EXIT_SUCCESS;
}
