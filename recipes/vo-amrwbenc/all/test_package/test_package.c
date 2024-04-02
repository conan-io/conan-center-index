#include <stdlib.h>
#include "vo-amrwbenc/enc_if.h"

int main(void)
{
    void* state = E_IF_init();
    E_IF_exit(state);

    return EXIT_SUCCESS;
}
