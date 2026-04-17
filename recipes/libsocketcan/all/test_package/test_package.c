#include <stdlib.h>
#include <stdio.h>

#include <libsocketcan.h>


int main() {
    printf("Test package for libsocketcan\n");
    (void)&can_do_start;
    return EXIT_SUCCESS;
}
