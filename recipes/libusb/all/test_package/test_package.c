#include <libusb.h>

int main(int argc, char *argv[]) {
    libusb_device **devs;

    int r = libusb_init(NULL);
    if (r < 0)
        return r;

    ssize_t cnt = libusb_get_device_list(NULL, &devs);
    if (cnt < 0)
        return (int)cnt;

    libusb_free_device_list(devs, 1);
    libusb_exit(NULL);

    return 0;
}
