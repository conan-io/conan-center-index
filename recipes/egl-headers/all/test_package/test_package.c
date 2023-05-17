#include "EGL/egl.h"
#include "EGL/eglext.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    EGLBoolean value = EGL_TRUE;
    printf("EGL_TRUE: %d\n", value);
    return EXIT_SUCCESS;
}
