#include <X11/Xlib.h>
#include <X11/Xutil.h>

#include <X11/extensions/dmxext.h>

#include <X11/Xauth.h>

#include <stdio.h>

int main() {
    Display *display = XOpenDisplay(NULL);

    if (!display) {
        printf("XOpenDisplay failed\n");
        return 0;
    }

    {
        int dmx_major = 0, dmx_minor = 0, dmx_patch = 0;
        if (DMXQueryVersion(display, &dmx_major, &dmx_minor, &dmx_patch))
            printf("DMXQueryVersion: %d.%d.%d\n", dmx_major, dmx_minor, dmx_patch);
    }

    {
        char *xau_file_name = XauFileName();
        if (xau_file_name)
            printf("XauFileName: %s\n", xau_file_name);
    }

    XCloseDisplay(display);
}
