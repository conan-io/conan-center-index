#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define QOI_IMPLEMENTATION
#include "qoi.h"

int main(void) {
    // 2x2 rgba sample image
    const uint8_t sample_img[] = {
        0x00, 0x00, 0x00, 0xff,
        0xff, 0x00, 0x00, 0xff,
        0x00, 0xff, 0x00, 0xff,
        0x00, 0x00, 0xff, 0xff,
    };

    qoi_desc desc;
    desc.width = 2;
    desc.height = 2;
    desc.channels = 4;
    desc.colorspace = QOI_SRGB;

    int out_len = 0;
    void* encoded_img = qoi_encode(sample_img, &desc, &out_len);
    if(encoded_img == NULL) {
        printf("Error encoding image\n");
        return EXIT_FAILURE;
    }

    qoi_desc desc2;
    void* decoded_img = qoi_decode(encoded_img, out_len, &desc2, 0);
    if(decoded_img == NULL) {
        printf("Error decoding image\n");
        return EXIT_FAILURE;
    }

    if(memcmp(sample_img, decoded_img, desc.width*desc.height*desc.channels) != 0) {
        printf("Decoded image mismatch\n");
        return EXIT_FAILURE;
    }

    if(desc.width != desc2.width || desc.height != desc2.height || desc.channels != desc2.channels || desc.colorspace != desc2.colorspace) {
        printf("Description mismatch\n");
        return EXIT_FAILURE;
    }

    printf("Image encoded and decoded successfully :)\n");

    return EXIT_SUCCESS;
}
