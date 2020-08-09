#include "mimalloc.h"

#include <stdlib.h>
#include <stdio.h>

int main() {
    void *data = malloc(1024);
    free(data);

    printf("mimalloc version %d\n", mi_version());
    mi_stats_print(nullptr);
    return 0;
}
