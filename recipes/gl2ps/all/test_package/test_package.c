#include <gl2ps.h>

#include <stdio.h>
#include <string.h>

int main(void) {
    /* No OpenGL context is available in CI, so only call functions that do not use OpenGL */
    GLint options = -1;

    printf("gl2ps %d.%d.%d\n", GL2PS_MAJOR_VERSION, GL2PS_MINOR_VERSION, GL2PS_PATCH_VERSION);

    if (gl2psGetOptions(&options) != GL2PS_UNINITIALIZED) {
        fprintf(stderr, "gl2psGetOptions should report an uninitialized state\n");
        return 1;
    }

    if (strcmp(gl2psGetFileExtension(GL2PS_PDF), "pdf") != 0) {
        fprintf(stderr, "unexpected file extension for PDF\n");
        return 1;
    }

    return 0;
}
