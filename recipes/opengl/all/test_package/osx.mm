#include "TargetConditionals.h"

#if TARGET_OS_TV || TARGET_OS_WATCH || TARGET_OS_IPHONE
#else
#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#endif

bool init_context()
{
#if TARGET_OS_TV || TARGET_OS_WATCH || TARGET_OS_IPHONE
    return true;
#else
    NSOpenGLPixelFormatAttribute pixelFormatAttributes[] =
    {
        NSOpenGLPFAColorSize, 24,
        NSOpenGLPFAAlphaSize, 8,
        NSOpenGLPFADoubleBuffer,
        0
    };
    NSOpenGLPixelFormat *pixelFormat = [[NSOpenGLPixelFormat alloc] initWithAttributes:pixelFormatAttributes];
    if (!pixelFormat)
        return false;

    NSOpenGLContext *context = [[NSOpenGLContext alloc] initWithFormat:pixelFormat shareContext:nil];
    if (!context)
        return false;
    [context makeCurrentContext];
    return true;
#endif
}
