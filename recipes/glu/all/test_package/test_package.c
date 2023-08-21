#include <stdio.h>

#ifdef __APPLE__
# include <OpenGL/glu.h>
#else
# ifdef _WIN32
#  include <windows.h>
# endif
# include <GL/glu.h>
#endif

int main()
{
    printf("GLU %s\n", gluGetString(GLU_VERSION));

    return 0;
}
