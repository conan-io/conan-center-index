#include <nsync.h>

static int int_is_zero (const void *v) {
    return (*(const int *)v == 0);
}

int main() {
    nsync_mu testing_mu;  /* protects fields below */
    int child_count;      /* count of testing_s structs whose base is this testing_base_s */

    nsync_mu_lock (&testing_mu);
    nsync_mu_wait (&testing_mu, &int_is_zero, &child_count, NULL);
    nsync_mu_unlock (&testing_mu);
    return 0;
}
