#include <stdio.h>
#include <stdlib.h>

#include "tommath.h"


int main(void) {
    mp_int a;

    mp_init(&a);
    mp_rand(&a, 4);
    printf("a = ");
    mp_fwrite(&a, 4, stdout);
    printf("\n");

    return EXIT_SUCCESS;
}
