#include "usb.h"

#include <stdlib.h>

int main() {
    usb_init();
    usb_find_busses();
    usb_find_devices();
    return EXIT_SUCCESS;
}
