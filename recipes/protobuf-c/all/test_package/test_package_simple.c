#include <stdio.h>
#include <stdlib.h>

#include "protobuf-c/protobuf-c.h"


int main(void) {
    printf("Protobuf-C version: %s\n", protobuf_c_version());
    return EXIT_SUCCESS;
}
