#include <stdlib.h>
#include <stdio.h>

#include <tomcrypt.h>

int main(void) {
    const char *msg = error_to_string(CRYPT_OK);
    printf("%s\n", msg);
    return EXIT_SUCCESS;
}
