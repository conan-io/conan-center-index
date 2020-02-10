#include "config.h"

#include <stdio.h>

int hello_from_c(void) {
    printf("Hello world (" PACKAGE_NAME ") from c!\n");
    return 0;
}
