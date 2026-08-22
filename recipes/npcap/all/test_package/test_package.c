#include <stdlib.h>

#include "pcap/pcap.h"

int main(void)
{
    printf(pcap_lib_version());
    return EXIT_SUCCESS;
}
