#include "libpkgconf/libpkgconf.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool error_callback(const char *msg, const pkgconf_client_t *client, const void *data) {
    printf("error callback: %s\n", msg);
    fflush(stdout);
    return 1; // 1/true means message handled
}

int main() {
    pkgconf_client_t client;
    memset(&client, 0, sizeof(client));

    pkgconf_client_init(&client, error_callback, NULL, pkgconf_cross_personality_default());

    pkgconf_error(&client, "%s:%d %s: %s", __FILE__, __LINE__, __FUNCTION__, "test error");

    pkgconf_client_deinit(&client);

    return 0;
}
