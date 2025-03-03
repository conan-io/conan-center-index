#include <vdpau/vdpau.h>
#include <vdpau/vdpau_x11.h>

#include <stddef.h>

void dummy() {
    vdp_device_create_x11(NULL, 0, NULL, NULL);
}

int main()
{
}
