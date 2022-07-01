#include <X11/Xlib.h>
#include <X11/Xutil.h>

#include <X11/Xauth.h>

#include <X11/SM/SMlib.h>

#include <stdio.h>

int main() {
    Display *display = XOpenDisplay(NULL);

    if (!display) {
        printf("XOpenDisplay failed\n");
        return 0;
    }

    {
        char *xau_file_name = XauFileName();
        if (xau_file_name)
            printf("XauFileName: %s\n", xau_file_name);
    }

    XCloseDisplay(display);
    SmcSetErrorHandler(NULL);
}
