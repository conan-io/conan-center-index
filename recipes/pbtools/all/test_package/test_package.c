#include <stdlib.h>

#include "pbtools.h"


struct foo_t {
    struct pbtools_message_base_t base;
    int32_t bar;
};

void foo_init(struct foo_t * foo_p, struct pbtools_heap_t *heap_p) {
    foo_p->base.heap_p = heap_p;
    foo_p->bar = 0;
}

void foo_encode_inner(struct pbtools_encoder_t *encoder_p, struct foo_t *foo_p) {
    pbtools_encoder_write_int32(encoder_p, 1, foo_p->bar);
}

int main() {
    int size;
    uint8_t workspace[64];
    uint8_t encoded[16];
    struct foo_t *foo_p;

    foo_p = pbtools_message_new(&workspace[0], sizeof(workspace), sizeof(struct foo_t), (pbtools_message_init_t)foo_init);
    foo_p->bar = 42;
    pbtools_message_encode(&foo_p->base, &encoded[0], sizeof(encoded), (pbtools_message_encode_inner_t)foo_encode_inner);

    return EXIT_SUCCESS;
}
