#include <stdio.h>
#include <hb.h>

int main() {
    hb_buffer_t *buffer = hb_buffer_create();
    if (buffer) {
        printf("HarfBuzz has been initialized successfully.\n");
        hb_buffer_destroy(buffer);
    } else {
        printf("Error: Unable to initialize HarfBuzz correctly.\n");
    }

    return 0;
}
