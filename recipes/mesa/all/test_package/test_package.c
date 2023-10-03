#include <stdlib.h>

#include <EGL/egl.h>
#include <EGL/eglmesaext.h>

int main(void) {
    if (EGL_DRM_BUFFER_FORMAT_ARGB2101010_MESA > 0) {
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}
