#include <stdlib.h>

#include <libweston/libweston.h>

int main() {
    struct weston_log_context *log_ctx = NULL;
    log_ctx = weston_log_ctx_create();
	if (!log_ctx) {
		return EXIT_FAILURE;
	}
    return EXIT_SUCCESS;
}
