#include <stdlib.h>
#include <stdio.h>

#include <systemd/sd-bus.h>

int main(void) {
    puts("check object path");
    if (sd_bus_object_path_is_valid("/valid/path")) {
        puts("ok");
        return EXIT_SUCCESS;
    }
    puts("failed");
    return EXIT_FAILURE;
}
