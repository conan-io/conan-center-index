#include <tgc.h>

static tgc_t gc;

static void example_function() {
    char *message = tgc_alloc(&gc, 64);
    strcpy(message, "No More Memory Leaks!");
}

int main(int argc, char **argv) {
    tgc_start(&gc, &argc);

    example_function();

    tgc_stop(&gc);

    return 0;
}
