#include <stdlib.h>
#include <libdecor.h>

int libdecor_state_get_content_width(struct libdecor_state *state);

int main(int argc, char **argv) {
    struct libdecor_state *state = libdecor_state_new(0, 0);
    int width = libdecor_state_get_content_width(state);
    free(state);
    if (width == 0) {
        return EXIT_SUCCESS;
    }

	return EXIT_FAILURE ;

}
