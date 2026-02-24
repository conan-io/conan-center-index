#include "tommath.h"

#include <stdio.h>
#include <stdlib.h>

int main(void) {
    mp_int a;
    mp_init(&a);
    mp_rand(&a, 30);
    printf("mp_init.used: %d\n", a.used);
    return EXIT_SUCCESS;
}
