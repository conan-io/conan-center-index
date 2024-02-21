#include <stdio.h>

#include <GL/glu.h>

int main()
{
    printf("GLU %s\n", gluGetString(GLU_VERSION));
    return 0;
}
