#include <stdio.h>

#include <EGL/egl.h>

int main()
{
    EGLint major = 0;
    EGLint minor = 0;
    EGLDisplay dpy = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    EGLBoolean b;
    if (dpy == EGL_NO_DISPLAY)
    {
        printf("No display available\n");
        return 0;
    }
    b = eglInitialize(dpy, &major, &minor);
    if(b != EGL_TRUE)
    {
        printf("could not initialize egl, error %d\n", eglGetError());
        return 0;
    }
    
    printf("egl version %d.%d\n", major, minor);   

    b = eglTerminate(dpy);
    if(b != EGL_TRUE)
    {
        printf("could not terminate egl %d\n", eglGetError());
        return 0;
    }
    
    return 0;
}
