#include <stdio.h>

#include "gsasl.h"

int main(int argc, char *argv[]) {
    Gsasl *ctx = NULL;
    int rc = gsasl_init (&ctx);
    if (rc != GSASL_OK) {
        printf(stderr, "gsasl_init failed\n");
        return rc;
    }
    printf("gsasl_init() result = GSASL_OK \n");
    return 0;
}
