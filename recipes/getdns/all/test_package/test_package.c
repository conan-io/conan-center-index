#include "getdns.h"

#include <stdio.h>
#include <stdlib.h>

#define CHECK(V) if ((V) != GETDNS_RETURN_GOOD) {   \
    fprintf(stderr, "Fail: " #V "!\n");             \
    return 1;                                       \
}

int main()
{
    getdns_context *context;
    CHECK(getdns_context_create(&context, 1));
    getdns_dict *info = getdns_context_get_api_information(context);
    if (info == NULL) {
        fprintf(stderr, "Could not get api information\n");
        return 1;
    }
    char *txt = getdns_pretty_print_dict(info);
    printf("%s\n", txt);
    free(txt);
    getdns_dict_destroy(info);
    getdns_context_destroy(context);
    return 0;
}
