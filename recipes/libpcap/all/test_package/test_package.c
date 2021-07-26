#include <stdlib.h>

#include "pcap.h"

int main(void)
{
    char errbuf[PCAP_ERRBUF_SIZE] = {0};
    bpf_u_int32 netp = 0;
    bpf_u_int32 maskp = 0;
    const char* dev = NULL;

    // device lookup
    dev = pcap_lookupdev(errbuf);
    if (dev != NULL) {
        if (pcap_lookupnet(dev, &netp, &maskp, errbuf) == -1) {
            fprintf(stderr, "Couldn't get netmask for device %s: %s\n", dev, errbuf);
        } else {
            fprintf(stdout, "Lookup success on device %s\n", dev);
        }
    } else {
        fprintf(stderr, "Couldn't lookup devices: %s\n", errbuf);
    }

    return EXIT_SUCCESS;
}
