#include <stdlib.h>
#include <stdio.h>

#include "glib.h"
#include "gmodule.h"
#include "gio/gio.h"


int main() {
    printf("glib %d.%d.%d\n", glib_major_version, glib_minor_version, glib_micro_version);
    printf("glib interface age: %d\n", glib_interface_age);
    printf("glib binary age: %d\n", glib_binary_age);

    GQueue *queue = g_queue_new();
    g_queue_free(queue);

    const gboolean supported = g_module_supported();
    if (supported) {
        printf("glib module supported: true\n");
    }
    else {
        printf("glib module supported: false\n");
    }


    GMutex m;
    g_mutex_init(&m);
    g_mutex_clear(&m);

    printf("type name for char: %s\n", g_type_name(G_TYPE_CHAR));

    return EXIT_SUCCESS;
}
