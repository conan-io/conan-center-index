#include <stdlib.h>

#include "avahi-compat-libdns_sd/dns_sd.h"
#include "avahi-core/log.h"


int main(void) {
    DNSServiceRef sdRef;
    DNSServiceErrorType err = DNSServiceBrowse(&sdRef, 0, 0, "_example._tcp", NULL, NULL, NULL);
    if (err == kDNSServiceErr_NoError)
    {
        avahi_log_error("DNSServiceBrowse succeeded\n");
        DNSServiceRefDeallocate(sdRef);
    }
    else
    {
        avahi_log_info("DNSServiceBrowse failed: %d\n", err);
    }
    return EXIT_SUCCESS;
}
