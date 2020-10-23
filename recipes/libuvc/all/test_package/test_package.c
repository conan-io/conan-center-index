#include <stdio.h>
#include <unistd.h>
#include <libuvc/libuvc.h>

int main()
{
	uvc_context_t *ctx;
	uvc_error_t res;
	uvc_device_t *dev;
	uvc_device_handle_t *devh;

	res = uvc_init(&ctx, NULL);

	if (res < 0) {
		uvc_perror(res, "uvc_init");
		return res;
	}

	puts("UVC initialized");

	res = uvc_find_device(
		ctx, &dev,
		0, 0, NULL);

	if (res < 0) {
		uvc_perror(res, "uvc_find_device");
	} else {
		puts("Device found");

		res = uvc_open(dev, &devh);

		if (res < 0) {
			uvc_perror(res, "uvc_open");
		} else {
			puts("Device opened");
			uvc_print_diag(devh, stderr);
			uvc_close(devh);
			puts("Device closed");
		}
		uvc_unref_device(dev);
	}

	uvc_exit(ctx);
	puts("UVC exited");

	return 0;
}
