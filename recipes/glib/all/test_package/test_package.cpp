#include <stdlib.h>
#include <stdio.h>

#include "glib.h"

int main(int argc, char** argv) {
    GQueue* queue = g_queue_new();

    if (!g_queue_is_empty(queue)) {
        return EXIT_FAILURE;
    }

    g_queue_push_tail(queue, const_cast<char *>("Alice"));
    g_queue_push_tail(queue, const_cast<char *>("Bob"));
    g_queue_push_tail(queue, const_cast<char *>("Fred"));

    printf("head: %s\n", (const char*) g_queue_peek_head(queue));
    printf("tail: %s\n", (const char*) g_queue_peek_tail(queue));
    printf("length: %d\n",  g_queue_get_length(queue));
    printf("pop: %s\n", (const char*) g_queue_pop_head(queue));
    printf("length: %d\n",  g_queue_get_length(queue));
    printf("head: %s\n", (const char*) g_queue_peek_head(queue));
    g_queue_push_head(queue, const_cast<char *>("Big Jim"));
    printf("length: %d\n",  g_queue_get_length(queue));
    printf("head: %s\n", (const char*) g_queue_peek_head(queue));
    g_queue_free(queue);

    return EXIT_SUCCESS;
}
