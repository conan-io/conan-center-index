#include <stdlib.h>

#ifdef MESA_TEST_PACKAGE_HAS_EGL
#include <EGL/egl.h>
#include <EGL/eglmesaext.h>
#endif

#ifdef _WIN32
#include <GL/gl.h>
#endif

int main(void) {
#if MESA_TEST_PACKAGE_HAS_EGL
    if (EGL_DRM_BUFFER_FORMAT_ARGB2101010_MESA <= 0) {
        return EXIT_FAILURE;
    }
#endif
#ifdef _WIN32
    if (glIsEnabledi(GL_DITHER, 0) != GL_TRUE) {
        return EXIT_FAILURE;
    }
    if (glGetError() != GL_NO_ERROR) {
        return EXIT_FAILURE;
    }
#endif
    return EXIT_SUCCESS;
}
