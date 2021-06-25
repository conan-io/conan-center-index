#include <miniupnpc/miniupnpc.h>

int main(void) {
    const char * multicastif = 0;
    const char * minissdpdpath = 0;
    int localport = UPNP_LOCAL_PORT_ANY;
    int ipv6 = 0;
    unsigned char ttl = 2;
    int error = 0;
    struct UPNPDev *devlist = upnpDiscover(2000, multicastif, minissdpdpath, localport, ipv6, ttl, &error);
    return 0;
}
