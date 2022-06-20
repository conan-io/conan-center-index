#include <iostream>

#ifdef __APPLE__

#include <OpenGL/gl.h>

#else

#ifdef _WIN32
#include <Windows.h>
#endif

#if defined(__linux__) or defined(__FreeBSD__)

bool init_context() { return true; }

#endif

#include <GL/gl.h>

#endif

bool init_context();

int main()
{
    if (!init_context())
    {
       // std::cerr << "failed to initialize OpenGL context!" << std::endl;
       // return -1;

       // Don't fail if we can't init the context - won't work on a headless CI
       // Instead, if we made it this far, then we were able to #include and link,
       // count that as a success!
       std::cout << "Linked test, but failed to initialize OpenGL context (headless platform?)" << std::endl;
       return 0;
    }
    const char * gl_vendor = (const char *) glGetString(GL_VENDOR);
    const char * gl_renderer = (const char *) glGetString(GL_RENDERER);
    const char * gl_version = (const char *) glGetString(GL_VERSION);
    const char * gl_extensions = (const char *) glGetString(GL_EXTENSIONS);
    std::cout << "GL_VENDOR: " << (gl_vendor ? gl_vendor : "(null)") << std::endl;
    std::cout << "GL_RENDERER: " << (gl_renderer ? gl_renderer : "(null)") << std::endl;
    std::cout << "GL_VERSION: " << (gl_version ? gl_version : "(null)") << std::endl;
    std::cout << "GL_EXTENSIONS: " << (gl_extensions ? gl_extensions : "(null)") << std::endl;
    return 0;
}
