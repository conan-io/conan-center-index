#include <libudev.h>
#include <iostream>

int main(int argc, char *argv[]) {
	static struct udev *udev_context = NULL;

	udev_context = udev_new();
	if (!udev_context) {
		std::cout << "udev context could not be created" << std::endl;
		return 1;
	} else {
		std::cout << "udev context created successfully" << std::endl;
	}

	return 0;
}
