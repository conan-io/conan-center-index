#include <stdio.h>

#ifdef __APPLE__
# include <OpenGL/gl.h>
# include <OpenGL/glu.h>
#else
# ifdef _WIN32
#  include <Windows.h>
# endif
# include <GL/gl.h>
# include <GL/glu.h>
#endif

int main()
{
    printf("GLU %s\n", gluGetString(GLU_VERSION));

    return 0;
}
