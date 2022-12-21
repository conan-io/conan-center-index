#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#include "wyhash.h"

int main(void) {
    uint64_t _wyp[4];
    make_secret(time(NULL), _wyp);
    char s[] = "fcdskhfjs";
    uint64_t h=wyhash(s, sizeof(s) / sizeof(s[0]), 0 ,_wyp);

    return 0;
}
