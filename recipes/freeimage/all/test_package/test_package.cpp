#include <iostream>

#include <FreeImage.h>

#if defined(FREEIMAGE_LIB) || !defined(WIN32)
#define NEED_INIT 1
#endif

void FreeImageErrorHandler(FREE_IMAGE_FORMAT fif, const char* message)
{
    std::cerr << "FreeImage error: " << message << std::endl;
}

int main(int argc, char** argv )
{
    if (argc < 2) {
        std::cerr << "Need at least one argument" << std::endl;
        return 1;
    }

#if NEED_INIT
    FreeImage_Initialise();
#endif

    FreeImage_SetOutputMessage(FreeImageErrorHandler);

    std::cout << "FreeImage " << FreeImage_GetVersion() << ", with:" << std::endl;

    for (int i = 0; i < FreeImage_GetFIFCount(); ++i)
    {
        std::cout << "\t- " << FreeImage_GetFIFExtensionList((FREE_IMAGE_FORMAT)i) << std::endl;
    }

    const char * image_file = argv[1];
    FREE_IMAGE_FORMAT fif = FIF_UNKNOWN;
    fif = FreeImage_GetFileType(image_file, 0);
    if (fif == FIF_UNKNOWN) {
        fif = FreeImage_GetFIFFromFilename(image_file);
    }
    if ((fif != FIF_UNKNOWN) && FreeImage_FIFSupportsReading(fif)) {
        FIBITMAP* dib = FreeImage_Load(fif, image_file, 0);
        if (dib)
        {
            FreeImage_Unload(dib);
        }
    }

#if NEED_INIT
    FreeImage_DeInitialise();
#endif

    return 0;
}
