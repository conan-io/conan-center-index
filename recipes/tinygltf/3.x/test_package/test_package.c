#include <tiny_gltf_v3.h>

int main(void) {
    tg3_error_stack errors;
    tg3_error_stack_init(&errors);
    tg3_error_stack_free(&errors);
    return 0;
}
