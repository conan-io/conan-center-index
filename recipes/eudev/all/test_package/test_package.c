#include <stdio.h>
#include <stdlib.h>
#include <libudev.h>


int main() {
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
