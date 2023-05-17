#include <stdio.h>

#include <GL/gl.h>


int main()
{
    const char * gl_vendor = (const char *) glGetString(GL_VENDOR);
    const char * gl_renderer = (const char *) glGetString(GL_RENDERER);
    const char * gl_version = (const char *) glGetString(GL_VERSION);
    const char * gl_extensions = (const char *) glGetString(GL_EXTENSIONS);
    printf( "GL_VENDOR: %s\n",  gl_vendor ? gl_vendor : "(null)");
    printf( "GL_RENDERER: %s\n",  gl_renderer ? gl_renderer : "(null)");
    printf( "GL_VERSION: %s\n",  gl_version ? gl_version : "(null)");
    printf( "GL_EXTENSIONS: %s\n",  gl_extensions ? gl_extensions : "(null)");
    return 0;
}
