#include <dns_sd.h>
#include <stdio.h>

int main()
{
    DNSServiceRef sdRef;
    DNSServiceErrorType err = DNSServiceBrowse(&sdRef, 0, 0, "_example._tcp", NULL, NULL, NULL);
    if (err == kDNSServiceErr_NoError)
    {
        printf("DNSServiceBrowse succeeded\n");
        DNSServiceRefDeallocate(sdRef);
    }
    else
    {
        printf("DNSServiceBrowse failed: %d\n", err);
    }
    return 0;
}
