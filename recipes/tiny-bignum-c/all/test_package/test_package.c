#include <bn.h>

#include <stdio.h>

void factorial(struct bn* n, struct bn* res) {
    struct bn tmp;

    bignum_assign(&tmp, n);
    bignum_dec(n);

    while (!bignum_is_zero(n)) {
        bignum_mul(&tmp, n, res);
        bignum_dec(n);
        bignum_assign(&tmp, res);
    }

    bignum_assign(res, &tmp);
}

int main(void) {
    struct bn num;
    struct bn result;
    char buf[8192];

    bignum_from_int(&num, 100);
    factorial(&num, &result);
    bignum_to_string(&result, buf, sizeof(buf));
    printf("factorial(100) using bignum = %s\n", buf);

    return 0;
}
