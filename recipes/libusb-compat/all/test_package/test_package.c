#include "usb.h"

#include <stdlib.h>


int main(int argc, char *argv[]) {
    usb_init();
    usb_find_busses();
    usb_find_devices();
    return EXIT_SUCCESS;
}
