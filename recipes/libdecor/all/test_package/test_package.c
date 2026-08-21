#include <stdlib.h>
#include <libdecor.h>

int main(void)
{
    struct libdecor_state *state = libdecor_state_new(0, 0);
    if (!state)
        return EXIT_FAILURE;
    libdecor_state_free(state);
    return EXIT_SUCCESS;
}
