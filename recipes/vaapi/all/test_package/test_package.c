#include <va/va.h>
#include <va/va_x11.h>

#include <X11/Xlib.h>

#include <stdio.h>

int main()
{
    VADisplay va_display;
    VAStatus status;
    int major, minor;
    Display * display = XOpenDisplay(NULL);
    if (!display)
    {
        printf("XOpenDisplay failed!\n");
        return 0;
    }
    va_display = vaGetDisplay(display);
    if (!va_display)
    {
        XCloseDisplay(display);
        printf("vaGetDisplay failed\n");
        return 0;
    }
    status = vaInitialize(va_display, &major, &minor);
    if (status == VA_STATUS_SUCCESS)
        printf("va version %d.%d\n", major, minor);
    else
    {
        XCloseDisplay(display);
        printf("vaInitialize failed\n");
        return 0;
    }
    vaTerminate(va_display);
    XCloseDisplay(display);
    return 0;
}
