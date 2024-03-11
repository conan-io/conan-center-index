#include "gpiod.h"

int main(int argc, char *argv[]) {
    struct gpiod_chip *chip;
    chip = gpiod_chip_open("/dev/gpiochip0");
    return 0;
}
