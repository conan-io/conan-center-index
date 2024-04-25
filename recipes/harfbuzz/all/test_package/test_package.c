#include <stdio.h>
#include <hb.h>

int main() {
    hb_buffer_t *buffer = hb_buffer_create();
    hb_buffer_destroy(buffer);

}
