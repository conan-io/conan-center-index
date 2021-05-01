#include <stdlib.h>
#include <stdio.h>

#include "glib.h"
#include "gmodule.h"
#include "gio/gio.h"

void test_gmodule()
{
    if (g_module_supported())
        printf("gmodule supported\n");
    else
        printf("gmodule not supported\n");
}

void test_glib()
{
    GQueue *queue = g_queue_new();

    if (!g_queue_is_empty(queue))
    {
        return;
    }

    g_queue_push_tail(queue, "Alice");
    g_queue_push_tail(queue, "Bob");
    g_queue_push_tail(queue, "Fred");

    printf("head: %s\n", (const char *)g_queue_peek_head(queue));
    printf("tail: %s\n", (const char *)g_queue_peek_tail(queue));
    printf("length: %d\n", g_queue_get_length(queue));
    printf("pop: %s\n", (const char *)g_queue_pop_head(queue));
    printf("length: %d\n", g_queue_get_length(queue));
    printf("head: %s\n", (const char *)g_queue_peek_head(queue));
    g_queue_push_head(queue, "Big Jim");
    printf("length: %d\n", g_queue_get_length(queue));
    printf("head: %s\n", (const char *)g_queue_peek_head(queue));
    g_queue_free(queue);
}

void test_gio()
{
    GInetAddress *add = g_inet_address_new_any(G_SOCKET_FAMILY_IPV4);
    printf("Any ipv4 address: %s\n", g_inet_address_to_string(add));
    g_object_unref(add);
}

void test_gthread()
{
    GMutex m;
    g_mutex_init(&m);
    g_mutex_lock(&m);
    g_mutex_unlock(&m);
    g_mutex_clear(&m);
}

void test_gobject()
{
    printf("type name for char: %s\n", g_type_name(G_TYPE_CHAR));
}

int main(int argc, char **argv)
{
    printf("glib %d.%d.%d\n", glib_major_version, glib_minor_version, glib_micro_version);
    printf("glib interface age: %d\n", glib_interface_age);
    printf("glib binary age: %d\n", glib_binary_age);
    test_glib();

    test_gmodule();

    test_gio();

    test_gthread();

    test_gobject();

    return EXIT_SUCCESS;
}
