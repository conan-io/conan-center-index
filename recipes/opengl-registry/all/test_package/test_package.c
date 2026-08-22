#include "GL/glcorearb.h"
#include "GL/glext.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("GL_GLEXT_VERSION: %d\n", GL_GLEXT_VERSION);
    GLenum value = GL_UNSIGNED_BYTE_3_3_2;
    printf("GL_UNSIGNED_BYTE_3_3_2: %x\n", value);
    return EXIT_SUCCESS;
}
