#include <stdio.h>
#include <krb5.h>

int main() {
    krb5_context context;
    krb5_error_code ret;

    ret = krb5_init_context(&context);
    if (ret) {
        fprintf(stderr, "Failed to initialize Kerberos context\n");
        return 1;
    }

    krb5_free_context(context);
    return 0;
}
