#include <stdlib.h>

#include "pcap/pcap.h"

int main(void)
{
    pcap_t* dev = pcap_open_dead(DLT_EN10MB, 65536);

    if (dev != NULL) {
        fprintf(stdout, "Open dead device success");
    }
    else {
        fprintf(stderr, "Couldn't open a dead device");
    }

    return EXIT_SUCCESS;
}
