#include <stdlib.h>
#include <stdio.h>
#include "libsoup/soup.h"

int main() {
    printf("libsoup version: %d.%d.%d\n", soup_get_major_version(), soup_get_minor_version(), soup_get_micro_version());
    return EXIT_SUCCESS;
}
