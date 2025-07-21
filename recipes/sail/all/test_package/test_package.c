#include <stdio.h>
#include <stdlib.h>
#include <sail/sail.h>

int main() {
    struct sail_image *image;
    sail_status_t status = sail_load_from_file("binary-file.bmp", &image);
    printf("Tried opening image with sail: status %d\nTEST SUCCEED\n", status);
}
