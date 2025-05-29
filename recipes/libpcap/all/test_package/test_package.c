#include <stdlib.h>

#include "pcap.h"

int main(void)
{
    printf("libpcap version: %s\n", pcap_lib_version());

    return EXIT_SUCCESS;
}
