#include <stdlib.h>
#include <stdio.h>
#include <plist/plist.h>


int main(void) {
    printf("plist version: %s\n", libplist_version());

    return EXIT_SUCCESS;
}
