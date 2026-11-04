#define MINICORO_IMPL
#include "minicoro.h"

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

void coro_entry(mco_coro* co) {
    printf("coroutine 1\n");
    mco_yield(co);
    printf("coroutine 2\n");
}

int main(void) {
    mco_desc desc = mco_desc_init(coro_entry, 0);
    desc.user_data = NULL;
    mco_coro* co;
    mco_create(&co, &desc);
    mco_destroy(co);

    return EXIT_SUCCESS;
}
