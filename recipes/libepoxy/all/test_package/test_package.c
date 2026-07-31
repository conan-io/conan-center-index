#include <stdio.h>
#include <stdlib.h>
#include "epoxy/gl.h"

int main(void) {
    printf("Epoxy extension found: %d\n", epoxy_extension_in_string("foo bar qux", "qux"));
    return EXIT_SUCCESS;
}