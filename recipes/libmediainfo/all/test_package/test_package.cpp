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
    MEDIAINFO_NS::MediaInfo mediainfo;

#if defined(LIBMEDIAINFO_SHARED)
    std::cout << "Is MediaInfo ready? " << mediainfo.IsReady() << "\n";
#endif

    std::string fakeVideoData = "FAKE DATA FOR TESTING\n";

    mediainfo.Open_Buffer_Init(fakeVideoData.size(), 0);
    mediainfo.Open_Buffer_Continue((unsigned char*)fakeVideoData.data(), fakeVideoData.size());
    mediainfo.Open_Buffer_Finalize();

    MEDIAINFO_NS::String info = mediainfo.Inform();
#ifdef UNICODE
    std::wcout << info;
#else
    std::cout << info;
#endif
    return 0;
}
