#include "getdns.h"

#include <stdlib.h>

int main() {
    getdns_context *context = NULL;
    getdns_context_create(&context, 0);
    getdns_context_destroy(context);
    return EXIT_SUCCESS;
}
