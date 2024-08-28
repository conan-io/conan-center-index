#include <stdio.h>
#include "jpeglib.h"
#include "transupp.h"

int main() {
    struct jpeg_decompress_struct info;
    struct jpeg_error_mgr err;
    info.err = jpeg_std_error(&err);
    jpeg_create_decompress(&info);
    printf("libjpeg test successful\n");
}
