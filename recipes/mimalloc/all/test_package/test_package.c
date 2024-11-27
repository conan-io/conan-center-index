#include "mimalloc.h"

#include <stdlib.h>
#include <stdio.h>

int main() {
    void *data = mi_malloc(32);

    printf("mimalloc version %d\n", mi_version());
    return EXIT_SUCCESS;
}
