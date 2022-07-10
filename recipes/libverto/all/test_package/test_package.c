#include "verto.h"

#include <stdio.h>
#include <stdlib.h>

struct timeout_info {
    int count;
};

static void on_timeout(verto_ctx *ctx, verto_ev *ev) {
    struct timeout_info *tinfo = (struct timeout_info *) verto_get_private(ev);
    tinfo->count++;
    printf("callback called: %d\n", tinfo->count);
    fflush(stdout);
    if (tinfo->count != 20) {
        verto_set_private(ev, NULL, NULL);
        verto_ev *ev_new = verto_add_timeout(ctx, VERTO_EV_FLAG_NONE, on_timeout, 50);
        verto_set_private(ev_new, tinfo, NULL);
    } else {
        verto_break(ctx);
    }
}

int main(int argc, char *argv[])
{
    verto_ctx *ctx;
    verto_ev *ev;

    if (argc < 2) {
        fprintf(stderr, "Need to pass the backend as an argument\n");
        return 1;
    }

    ctx = verto_new(argv[1], VERTO_EV_TYPE_TIMEOUT);
    if (ctx == NULL) {
        fprintf(stderr, "verto_new failed\n");
        return 1;
    }
    struct timeout_info *tinfo = (struct timeout_info*) malloc(sizeof(struct timeout_info));
    tinfo->count = 0;
    ev = verto_add_timeout(ctx, VERTO_EV_FLAG_NONE, on_timeout, 50);
    if (ev == NULL) {
        fprintf(stderr, "verto_add_timeout failed\n");
        return 1;
    }
    verto_set_private(ev, tinfo, NULL);

    verto_run(ctx);
    free(tinfo);

    verto_free(ctx);
//    verto_cleanup();  // <= munmap_chunk(): invalid pointer here
    return 0;
}
