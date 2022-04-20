#include "krb5.h"

#include <stdio.h>

int
main(int argc, char **argv)
{
    krb5_context context;
    int ret = krb5_init_context(&context);
    if (ret != 0) {
        fprintf(stderr, "krb5_init_context failed\n");
        return 1;
    }
    krb5_free_context(context);
    return 0;
}
