#define _POSIX_C_SOURCE 200112L
#include <stdlib.h>
#include <wlr/backend.h>
#include <wlr/util/log.h>

int main(void) {
	wlr_log_init(WLR_ERROR, NULL);
	struct wl_display *display = wl_display_create();
	struct wlr_backend *backend = wlr_backend_autocreate(wl_display_get_event_loop(display), NULL);
	if (!backend) {
		return EXIT_FAILURE;
	}
	wl_display_destroy(display);
    return EXIT_SUCCESS;
}
