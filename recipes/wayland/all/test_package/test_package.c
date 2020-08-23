#include <stdio.h>
#include <stdlib.h>
#include <wayland-client.h>

int main(int argc, char **argv) {

    struct wl_display *display = wl_display_connect(NULL);
    if (display == NULL) {
	    fprintf(stderr, "Can't connect to display\n");
    }
    else
    {
        printf("connected to display\n");

        wl_display_disconnect(display);
        printf("disconnected from display\n");
    }
    
    exit(0);
}
