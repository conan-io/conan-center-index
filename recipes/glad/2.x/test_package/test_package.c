#include "glad/gl.h"

#include <stdio.h>

int main() {
    int version = gladLoaderLoadGL();
    printf("GL %d.%d\n", GLAD_VERSION_MAJOR(version), GLAD_VERSION_MINOR(version));
    gladLoaderUnloadGL();

    return 0;
}
