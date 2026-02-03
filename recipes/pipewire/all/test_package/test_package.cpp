#include <cstdlib>
#include <pipewire/pipewire.h>


int main(void) {
    struct pw_context *ctx;
    struct pw_core *core;
	struct pw_loop *loop;

	pw_init(0, NULL);
	loop = pw_loop_new(NULL);
	ctx = pw_context_new(loop, NULL, 0);
    core = pw_context_connect(ctx, NULL, 0);

	pw_loop_enter(loop);
	pw_loop_iterate(loop, -1);
	pw_loop_leave(loop);
	pw_core_disconnect(core);
    pw_context_destroy(ctx);
	pw_loop_destroy(loop);

    return EXIT_SUCCESS;
}
