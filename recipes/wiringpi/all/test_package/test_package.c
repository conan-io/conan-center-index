#include <stdio.h>
#include <stdlib.h>

#include "wiringPi.h"

int main(void) {
    int major = 0;
    int minor = 0;
    wiringPiVersion(&major, &minor);
    printf("WiringPi version: %d.%d\n", major, minor);

    return EXIT_SUCCESS;
}
