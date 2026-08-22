#include <stdio.h>
#include <stdlib.h>

#ifdef _MSC_VER
#  include <windows.h>
#endif
#ifdef __APPLE__
#  include <OpenGL/OpenGL.h>
#  include <OpenGL/gl.h>
#else
#  include <GL/gl.h>
#endif
#include <GL/glext.h>

int main()
{
    printf("GL_GLEXT_VERSION: %d\n", GL_GLEXT_VERSION);
    return EXIT_SUCCESS;
}
