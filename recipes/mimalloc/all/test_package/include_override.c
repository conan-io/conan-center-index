#include "mimalloc-override.h"

#include <stdio.h>

int main() {
    void *data = malloc(1024);
    free(data);

    printf("mimalloc version %d\n", mi_version());
    return 0;
}
