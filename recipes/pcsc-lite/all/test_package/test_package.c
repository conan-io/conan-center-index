#include <stdio.h>
#include <stdlib.h>
#include <winscard.h>


int main() {
    pcsc_stringify_error(SCARD_S_SUCCESS);

    return EXIT_SUCCESS;
}
