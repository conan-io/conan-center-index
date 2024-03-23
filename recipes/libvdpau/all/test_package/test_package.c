#include <vdpau/vdpau.h>
#include <vdpau/vdpau_x11.h>

#include <X11/Xlib.h>

#include <stdio.h>

int main()
{
    VdpDevice device;
    VdpGetProcAddress * get_proc_address;
    VdpGetInformationString * get_information_string;
    VdpGetApiVersion * get_api_version;
    VdpStatus status;
    Display * display = XOpenDisplay(NULL);
    if (!display)
    {
        printf("XOpenDisplay failed!\n");
        return 0;
    }
    status = vdp_device_create_x11(display, 0, &device, &get_proc_address);
    if (status != VDP_STATUS_OK)
    {
        XCloseDisplay(display);
        printf("vdp_device_create_x11 failed\n");
        return 0;
    }
    status = get_proc_address(device, VDP_FUNC_ID_GET_INFORMATION_STRING, (void**) &get_information_string);
    if (status == VDP_STATUS_OK)
    {
        char const * information_string;
        status = get_information_string(&information_string);
        if (status == VDP_STATUS_OK)
            printf("VDPAU information string: %s\n", information_string);
    }
    status = get_proc_address(device, VDP_FUNC_ID_GET_API_VERSION, (void**) &get_api_version);
    if (status == VDP_STATUS_OK)
    {
        uint32_t api_version;
        status = get_api_version(&api_version);
        if (status == VDP_STATUS_OK)
            printf("VDPAU API version: %d\n", api_version);
    }
    XCloseDisplay(display);
    return 0;
}
