#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <libudev.h>

#define BLOCK_SIZE 512

int main()
{
	struct udev *udev;
	struct udev_device *dev;
	struct udev_enumerate *enumerate;
	struct udev_list_entry *devices, *dev_list_entry;

	/* create udev object */
	udev = udev_new();
	if (!udev) {
		fprintf(stderr, "Cannot create udev context.\n");
		return 0;
	}

	/* create enumerate object */
	enumerate = udev_enumerate_new(udev);
	if (!enumerate) {
		fprintf(stderr, "Cannot create enumerate context.\n");
		return 0;
	}

	udev_enumerate_add_match_subsystem(enumerate, "block");
	udev_enumerate_scan_devices(enumerate);

	/* fillup device list */
	devices = udev_enumerate_get_list_entry(enumerate);
	if (!devices) {
		fprintf(stderr, "Failed to get device list.\n");
		return 0;
	}

	udev_list_entry_foreach(dev_list_entry, devices) {
		const char *path, *tmp;
		unsigned long long disk_size = 0;
		unsigned short int block_size = BLOCK_SIZE;

		path = udev_list_entry_get_name(dev_list_entry);
		dev = udev_device_new_from_syspath(udev, path);

		/* skip if device/disk is a partition or loop device */
		if (strncmp(udev_device_get_devtype(dev), "partition", 9) != 0 &&
		    strncmp(udev_device_get_sysname(dev), "loop", 4) != 0) {
			printf("I: DEVNODE=%s\n", udev_device_get_devnode(dev));
			printf("I: KERNEL=%s\n", udev_device_get_sysname(dev));
			printf("I: DEVPATH=%s\n", udev_device_get_devpath(dev));
			printf("I: DEVTYPE=%s\n", udev_device_get_devtype(dev));

			tmp = udev_device_get_sysattr_value(dev, "size");
			if (tmp)
				disk_size = strtoull(tmp, NULL, 10);

			tmp = udev_device_get_sysattr_value(dev, "queue/logical_block_size");
			if (tmp)
				block_size = atoi(tmp);

			printf("I: DEVSIZE=");
			if (strncmp(udev_device_get_sysname(dev), "sr", 2) != 0)
				printf("%lld GB\n", (disk_size * block_size) / 1000000000);
			else
				printf("n/a\n");
		}

		/* free dev */
		udev_device_unref(dev);
	}
	/* free enumerate */
	udev_enumerate_unref(enumerate);
	/* free udev */
	udev_unref(udev);

	return 0;
}
