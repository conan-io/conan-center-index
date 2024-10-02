#include <stdio.h>
#include <stdlib.h>
#include <sail/sail.h>

int main() {
    struct sail_image *image;
    sail_status_t status = sail_load_from_file("binary-file.bmp", &image);
    printf("Error - file not found generate:  status %d\n", status);
}
