#include <stdlib.h>
#include <stdio.h>

#include <basu/sd-bus.h>

int main(void) {
    char *id = NULL;
    int ret = 0;

    puts("decode object path");
    ret = sd_bus_path_decode("/foo/bar", "/foo", &id);
    free(id);
    if (ret > 0) {
        puts("ok");
        return EXIT_SUCCESS;
    }
    puts("failed");
    return EXIT_FAILURE;
}
