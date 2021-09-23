
#include <stdio.h>
#include <wayland-client.h>
#include "xdg-shell-client-protocol.h"

// TODO: Need help to write actual test here 

int main(void)
{
    struct wl_display *display = wl_display_connect(NULL);
    if (display) {
        printf("Connected!\n");
        wl_display_disconnect(display);
    } else {
        printf("Error connecting ;(\n");
    }
    return 0;
}
