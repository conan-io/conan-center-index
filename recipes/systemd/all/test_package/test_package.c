#include <stdlib.h>

#include <systemd/sd-bus.h>

int main(void) {
    sd_bus_object_path_is_valid("/valid/path");
    return EXIT_SUCCESS;
}
