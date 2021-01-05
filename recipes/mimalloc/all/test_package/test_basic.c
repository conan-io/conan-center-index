#include "mimalloc.h"

#include <stdlib.h>
#include <stdio.h>

int main() {
    void *data = mi_malloc(1024);
    mi_free(data);

    printf("mimalloc version %d\n", mi_version());
    mi_stats_print_out(NULL, NULL);
    return 0;
}
