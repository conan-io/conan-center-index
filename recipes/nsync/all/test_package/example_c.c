#include <nsync.h>

int main() {
    nsync_mu testing_mu;
    nsync_mu_init (&testing_mu);
    nsync_mu_lock (&testing_mu);
    nsync_mu_unlock (&testing_mu);
    return 0;
}
