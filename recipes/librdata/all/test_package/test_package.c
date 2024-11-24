#include "rdata.h"

static int handle_table(const char *name, void *ctx) {
    printf("Read table: %s\n", name);

    return 0;
}