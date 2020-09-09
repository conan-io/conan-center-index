#include "proxy.h"

#include <stdio.h>
#include <stdlib.h>

int main()
{
    pxProxyFactory *factory = px_proxy_factory_new();
    if (factory == NULL) {
        fprintf(stderr, "px_proxy_factory_new failed\n");
        return 1;
    }
    char **res = px_proxy_factory_get_proxies(factory, "http://www.conan.io");
    for(char **item = res; *item; ++item) {
        printf("- %s\n", *item);
    }
    px_proxy_factory_free(factory);
    return 0;
}
