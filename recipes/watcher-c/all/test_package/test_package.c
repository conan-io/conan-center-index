#include "wtr/watcher-c.h"
#include <stdio.h>

void callback(struct wtr_watcher_event event, void* _ctx) {
    printf(
        "path name: %s, effect type: %d path type: %d, effect time: %ld, associated path name: %s\n",
        event.path_name,
        event.effect_type,
        event.path_type,
        event.effect_time,
        event.associated_path_name ? event.associated_path_name : ""
    );
}

int main() {
    void* watcher = wtr_watcher_open(".", callback, NULL);
    wtr_watcher_close(watcher);
    return 0;
}
