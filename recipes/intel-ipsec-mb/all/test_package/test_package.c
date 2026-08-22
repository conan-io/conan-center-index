#include "intel-ipsec-mb.h"

#include <stdio.h>
#include <stdlib.h>

int main() {
    const char * version = NULL;

    version = imb_get_version_str();
    printf("Intel IPSec MB Version: %s\n", version);

    return EXIT_SUCCESS;
}
