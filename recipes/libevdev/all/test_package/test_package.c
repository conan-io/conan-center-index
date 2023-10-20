#include <stddef.h>

#include <libevdev/libevdev.h>

int main(void) {
	libevdev_new_from_fd(0, NULL);
    return 0;
}
