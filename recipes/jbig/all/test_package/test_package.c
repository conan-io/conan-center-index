#include <stdlib.h>

#include "jbig.h"

int main() {
    struct jbg_dec_state state;

    jbg_dec_init(&state);
    jbg_dec_getplanes(&state);
    jbg_dec_free(&state);

    return EXIT_SUCCESS;
}
