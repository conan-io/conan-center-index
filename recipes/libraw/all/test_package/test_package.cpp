#include <libraw/libraw.h>
#include <libraw/libraw_version.h>
#include <iostream>

int main()
{
    std::cout << libraw_version() << "\n";
    #if LIBRAW_MAJOR_VERSION >= 0 && LIBRAW_MINOR_VERSION >= 22
        std::cout << "Maximum Canon CR3/CRM file size: " << LIBRAW_MAX_CR3_RAW_FILE_SIZE << "\n";
    #endif
    return 0;
}
