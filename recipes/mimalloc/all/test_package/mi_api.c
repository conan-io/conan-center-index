#include "mimalloc.h"

#include <stdlib.h>
#include <stdio.h>

int main() {
    void *data = mi_malloc(1024);

    printf("mimalloc version %d\n", mi_version());
    return 0;
}
