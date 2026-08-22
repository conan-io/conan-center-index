#include <stdio.h>
#include <stdlib.h>
#include "bzlib.h"


int main(void) {
    char buffer [256] = {0};
    unsigned int size = 256;
    const char* version = BZ2_bzlibVersion();
    printf("Bzip2 version: %s\n", version);
    BZ2_bzBuffToBuffCompress(buffer, &size, "conan-package-manager", 21, 1, 0, 1);
    printf("Bzip2 compressed: %s\n", buffer);
    return EXIT_SUCCESS;
}
