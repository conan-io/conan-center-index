#include <iostream>

#include <FreeImage.h>

#if defined(FREEIMAGE_LIB) || !defined(WIN32)
#define NEED_INIT 1
#endif

void FreeImageErrorHandler(FREE_IMAGE_FORMAT fif, const char* message)
{
    std::cerr << "FreeImage error: " << message << std::endl;
}

int main(int argc, char** argv ) {

#if NEED_INIT
    FreeImage_Initialise();
#endif

    FreeImage_SetOutputMessage(FreeImageErrorHandler);
    std::cout << "FreeImage " << FreeImage_GetVersion() << std::endl;

#if NEED_INIT
    FreeImage_DeInitialise();
#endif

    return 0;
}
