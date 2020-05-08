#include <stdio.h>
#include <mpir.h>

void foo(mpz_t result, const mpz_t param, unsigned long n)
{
    unsigned long i;
    mpz_mul_ui(result, param, n);
    for (i = 1; i < n; i++)
        mpz_add_ui(result, result, i * 7);
}

int main(void)
{
    mpz_t r, n;
    mpz_init(r);
    mpz_init_set_str(n, "123456", 0);
    foo(r, n, 20L);
    gmp_printf("%Zd\n", r);
    return 0;
}
