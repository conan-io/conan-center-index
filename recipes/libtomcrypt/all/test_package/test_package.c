#include <stdio.h>
#include <stdlib.h>
#include <tomcrypt.h>

int main(void) {
    const char *msg_ok = error_to_string(CRYPT_OK);
    printf("Tomcrypt test package: %s\n", msg_ok);
    return EXIT_SUCCESS;
}
