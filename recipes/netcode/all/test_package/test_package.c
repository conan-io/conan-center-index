#include <stdlib.h>
#include <stdio.h>
#include <netcode.h>


int main(void) {
    struct netcode_address_t address;
    netcode_parse_address("127.0.0.1:40000", &address);
    printf("netcode %s: port %d\n", NETCODE_VERSION_FULL, (int) address.port);
    return EXIT_SUCCESS;
}
