#include "tommath.h"

#include <stdio.h>
#include <stdlib.h>

#define check(V)                            \
    if ((V) != MP_OKAY) {                   \
        fprintf(stderr, #V " FAILURE\n");   \
        return 1;                           \
    }

int main() {
    mp_int a, b, c;

    check(mp_init(&a));
    check(mp_init(&b));
    check(mp_init(&c));

    check(mp_rand(&a, 30));
    check(mp_rand(&b, 30));

    check(mp_add(&a, &b, &c));

    printf("a = ");
    check(mp_fwrite(&a, 10, stdout));
    printf("\nb = ");
    check(mp_fwrite(&b, 10, stdout));
    printf("\na + b = ");
    check(mp_fwrite(&c, 10, stdout));
    printf("\n");

    mp_clear_multi(&a, &b, &c, NULL);
    return 0;
}
