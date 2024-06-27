#include <stdio.h>

// #define _GNU_SOURCE
#include "neco.h"

void coroutine(int argc, void *argv[]) {
    printf("main coroutine started\n");
}

int main(int argc, char *argv[]) {
    neco_start(coroutine, 0);
    return 0;
}
