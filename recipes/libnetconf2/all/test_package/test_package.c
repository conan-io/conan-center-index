#include <stdio.h>
#include <stdlib.h>
#include <libnetconf2/netconf.h>
#include <libnetconf2/log.h>
#include <libnetconf2/session_client.h>

int main(void) {
    nc_client_init();
    nc_client_destroy();
    printf("Conan Test Package: libnetconf2 OK\n");
    return EXIT_SUCCESS;
}
