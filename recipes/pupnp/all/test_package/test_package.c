#include <stdio.h>
#include <stdlib.h>
#include <upnp.h>

int main()
{
    int ret = UpnpInit2(NULL, 0);
    if (ret != UPNP_E_SUCCESS)
    {
        return EXIT_FAILURE;
    }
    int port = UpnpGetServerPort();
    printf("Bound at %s:%d\n", UpnpGetServerIpAddress(), port);
    return EXIT_SUCCESS;
}
