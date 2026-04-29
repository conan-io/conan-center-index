#include <cstdlib>
#include "AMF/core/Version.h"

int main(void) {
    printf("AMF version: %d.%d\n", AMF_VERSION_MAJOR, AMF_VERSION_MINOR);
    return EXIT_SUCCESS;
}

