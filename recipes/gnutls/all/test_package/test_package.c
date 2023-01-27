#include <stdlib.h>
#include <gnutls/gnutls.h>

int main (void) {
    int result = 0;
    gnutls_session_t session;

    gnutls_global_init();
    gnutls_global_set_log_level(0);

    gnutls_init(&session, GNUTLS_SERVER);
    gnutls_deinit(session);
    gnutls_global_deinit();

    return EXIT_SUCCESS;
}
