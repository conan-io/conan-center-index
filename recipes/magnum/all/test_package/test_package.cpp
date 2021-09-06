/*
Example taken from 'magnum-bootstrap' repository 
at https://github.com/mosra/magnum-bootstrap/tree/windowless.
*/

#include <iostream>
#include <Magnum/Magnum.h>

#ifdef MAGNUM_TARGET_HEADLESS
#include <Magnum/Platform/WindowlessEglApplication.h>
#elif defined(CORRADE_TARGET_IOS)
#include <Magnum/Platform/WindowlessIosApplication.h>
#elif defined(CORRADE_TARGET_APPLE)
#include <Magnum/Platform/WindowlessCglApplication.h>
#elif defined(CORRADE_TARGET_UNIX)
#if !defined(MAGNUM_TARGET_GLES) || defined(MAGNUM_TARGET_DESKTOP_GLES)
#include <Magnum/Platform/WindowlessGlxApplication.h>
#else
#include <Magnum/Platform/WindowlessEglApplication.h>
#endif
#elif defined(CORRADE_TARGET_WINDOWS)
#if !defined(MAGNUM_TARGET_GLES) || defined(MAGNUM_TARGET_DESKTOP_GLES)
#include <Magnum/Platform/WindowlessWglApplication.h>
#else
#include <Magnum/Platform/WindowlessWindowsEglApplication.h>
#endif
#else
#error no windowless application available on this platform
#endif

using namespace Magnum;

class MyApplication: public Platform::WindowlessApplication {
    public:
        explicit MyApplication(const Arguments& arguments);

        int exec() override;
};

MyApplication::MyApplication(const Arguments& arguments): Platform::WindowlessApplication{arguments} {
    /* TODO: Add your initialization code here */
}

int MyApplication::exec() {
    /* TODO: Add your processing code here */
    std::cout << "Magnum working\n";
    return 0;
}

MAGNUM_WINDOWLESSAPPLICATION_MAIN(MyApplication)
