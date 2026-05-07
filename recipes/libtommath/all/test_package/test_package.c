#include <stdio.h>
#include <stdlib.h>
#include "tommath.h"

int main(void) {
    mp_int a;
    mp_init(&a);
    printf("mp_init.used: %d\n", a.used);
    return EXIT_SUCCESS;
}
