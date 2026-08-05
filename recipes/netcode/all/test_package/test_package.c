#include <netcode.h>

#include <stdio.h>

int main(void)
{
    struct netcode_address_t address;

    if (netcode_init() != NETCODE_OK)
    {
        printf("failed to initialize netcode\n");
        return 1;
    }

    if (netcode_parse_address("127.0.0.1:40000", &address) != NETCODE_OK
         || address.type != NETCODE_ADDRESS_IPV4 || address.port != 40000)
    {
        printf("failed to parse address\n");
        netcode_term();
        return 1;
    }

    printf("netcode %s: parsed 127.0.0.1:%d\n", NETCODE_VERSION_FULL, (int) address.port);

    netcode_term();

    return 0;
}

