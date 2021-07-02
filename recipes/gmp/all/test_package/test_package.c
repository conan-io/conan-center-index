#include <gmp.h>

#include <stdio.h>
#include <stdlib.h>

int main (void) {
    mpz_t a,b,c;
    mpz_init_set_str(a, "1234", 10);
    mpz_init_set_str(b, "4321", 10);
    mpz_init(c);

    mpz_add(c, a, b);

    char *a_str = mpz_get_str(NULL, 10, a);
    char *b_str = mpz_get_str(NULL, 10, b);
    char *c_str = mpz_get_str(NULL, 10, c);

    printf("%s + %s = %s\n", a_str, b_str, c_str);

    free(a_str);
    free(b_str);
    free(c_str);

    return EXIT_SUCCESS;
}
