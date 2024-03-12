#include "chunkio/chunkio.h"
#include <stdio.h>

static int log_cb(struct cio_ctx *ctx, int level, const char *file, int line,
                  char *str)
{
    (void) ctx;

    printf("[cio-test-fs] %-60s => %s:%i\n",  str, file, line);
    return 0;
}

int main() {
    int flags = CIO_CHECKSUM;
    struct cio_ctx *ctx = cio_create(NULL, log_cb, CIO_LOG_INFO, flags);

    cio_destroy(ctx);

    return 0;
}
