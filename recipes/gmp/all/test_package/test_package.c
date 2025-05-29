#include <gmp.h>

int main (void) {
    mpz_t a;
    mpz_init(a);
    mpz_clear(a);

    return 0;
}
