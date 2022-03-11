#include "i2c/smbus.h"

#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Need an argument.\n");
        return 1;
    }
    int fd = open(argv[1], O_RDWR);
    if (fd <= 0) {
        fprintf(stderr, "Could not open %s.\n", argv[1]);
        return 2;
    }

    // Do more checks ...

    int res = i2c_smbus_write_byte(fd, 137);
    if (res < 0) {
        fprintf(stderr, "i2c_smbus_write_byte failed.\n");
        return 3;
    }

    res = close(fd);
    if (res < 0) {
        fprintf(stderr, "close failed.\n");
        return 4;
    }
}
