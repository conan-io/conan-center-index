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
    struct cio_options options;
    cio_options_init(&options);
    options.flags = CIO_CHECKSUM;
    options.log_level = CIO_LOG_INFO;
    struct cio_ctx *ctx = cio_create(&options);

    cio_destroy(ctx);

    return 0;
}
