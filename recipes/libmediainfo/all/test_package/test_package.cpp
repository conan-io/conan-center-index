#if defined(LIBMEDIAINFO_SHARED)
# include "MediaInfoDLL/MediaInfoDLL.h"
# define MEDIAINFO_NS MediaInfoDLL
#else
# include "MediaInfo/MediaInfo.h"
# define MEDIAINFO_NS MediaInfoLib
#endif
#include "ZenLib/Ztring.h"

#include <iostream>

int main(int argc, const char *argv[]) {
    if (argc < 2) {
        std::cerr << "Need at least one argument\n";
        return 1;
    }
    MEDIAINFO_NS::MediaInfo mediainfo;

#if defined(LIBMEDIAINFO_SHARED)
    std::cout << "Is MediaInfo ready? " << mediainfo.IsReady() << "\n";
#endif

    ZenLib::Ztring videofile(argv[1]);
    size_t opened = mediainfo.Open(videofile.To_Unicode());
    if (!opened) {
        std::cerr << "Open failed\n";
        return 1;
    }
    MEDIAINFO_NS::String info = mediainfo.Inform();
#ifdef UNICODE
    std::wcout << info;
#else
    std::cout << info;
#endif
    return 0;
}
