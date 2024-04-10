#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <libudev.h>
#include <libinput.h>

static int
open_restricted(const char *path, int flags, void *user_data)
{
	int fd = open(path, flags);
	return fd < 0 ? -1 : fd;
}

static void
close_restricted(int fd, void *user_data)
{
	close(fd);
}

static const struct libinput_interface interface = {
	.open_restricted = open_restricted,
	.close_restricted = close_restricted,
};

int main(void) {
	bool grab = false;
    struct libinput *li;
	struct udev *udev = udev_new();
	if (!udev) {
		fprintf(stderr, "Failed to initialize udev\n");
		return EXIT_FAILURE;
	}

	li = libinput_udev_create_context(&interface, &grab, udev);
	if (!li) {
		fprintf(stderr, "Failed to initialize libinput context from udev\n");
        udev_unref(udev);
        return EXIT_FAILURE;
	}

	if (libinput_udev_assign_seat(li, "seat0")) {
		fprintf(stderr, "Failed to set seat\n");
		libinput_unref(li);
		li = NULL;
        udev_unref(udev);
        return EXIT_FAILURE;
	}

    udev_unref(udev);
	return EXIT_SUCCESS;
}
