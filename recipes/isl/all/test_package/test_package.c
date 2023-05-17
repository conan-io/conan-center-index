#include "isl/ctx.h"


int main() {
    isl_ctx *ctx = isl_ctx_alloc();

    isl_ctx_free(ctx);
    return 0;
}
