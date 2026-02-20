#include <stdio.h>
#include <stdlib.h>
#include "epoxy/gl.h"

int main(void) {
    printf("Epoxy GL Version: %d\n", epoxy_gl_version());
    return EXIT_SUCCESS;
}