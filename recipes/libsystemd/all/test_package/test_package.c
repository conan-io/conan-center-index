#include <stdlib.h>
#include <stdio.h>
#include <libudev.h>

#include <systemd/sd-bus.h>

int main(void) {
    puts("check object path");
    if (sd_bus_object_path_is_valid("/valid/path")) {
        puts("ok");
        return EXIT_SUCCESS;
    }
    puts("failed");
    return EXIT_FAILURE;

// Test udev
    struct udev *udev;
    struct udev_enumerate *enumerate;

    udev = udev_new();
    if (!udev) {
        fprintf(stderr, "Cannot create udev context.\n");
        return 1;
    }

    enumerate = udev_enumerate_new(udev);
    if (!enumerate) {
        fprintf(stderr, "Cannot create enumerate context.\n");
    }

    udev_enumerate_unref(enumerate);
    udev_unref(udev);

    return EXIT_SUCCESS;
}
