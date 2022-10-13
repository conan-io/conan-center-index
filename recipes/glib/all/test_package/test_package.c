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

    g_module_supported();

    GMutex m;
    g_mutex_init(&m);
    g_mutex_clear(&m);

    printf("type name for char: %s\n", g_type_name(G_TYPE_CHAR));

    return EXIT_SUCCESS;
}
