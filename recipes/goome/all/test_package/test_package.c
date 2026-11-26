#define GOOME_IMPLEMENTATION
#include "goome.h"

#include <stdio.h>

int main(void) {
    int err = 0;
    goome *g = goome_open(&(goome_opts){.mode = GOOME_MODE_OFFSCREEN, .width = 64, .height = 32}, &err);
    if (!g) {
        printf("goome %s, offscreen open failed %d\n", GOOME_VERSION, err);
        return 1;
    }
    printf("goome %s, offscreen ok\n", GOOME_VERSION);
    goome_close(g);
    return 0;
}
