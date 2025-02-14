#include <stdlib.h>
#include <stdio.h>

#include <sframe-api.h>


int main(void) {
    const char* error_msg = sframe_errmsg(SFRAME_ERR_VERSION_INVAL);
    printf("Conan test package - binutils error message as validation: %s\n", error_msg);

    return EXIT_SUCCESS;
}
