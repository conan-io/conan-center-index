#include <iostream>
#include <miniupnpc.h>

int main() {
    int error = 0;
    //get a list of upnp devices (asks on the broadcast address and returns the responses)
    struct UPNPDev *upnp_dev = upnpDiscover(20,    //timeout in milliseconds
                                            NULL,  //multicast address, default = "239.255.255.250"
                                            NULL,  //minissdpd socket, default = "/var/run/minissdpd.sock"
                                            0,     //source port, default = 1900
                                            0,
                                            0,
                                            &error); //error output
    freeUPNPDevlist(upnp_dev);
    return 0;
}
