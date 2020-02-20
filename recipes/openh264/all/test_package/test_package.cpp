#include <iostream>
#include <cstdlib>
#include <wels/codec_api.h>

int main()
{
    OpenH264Version version = WelsGetCodecVersion();
    std::cout << "OpenH264 version: " << version.uMajor << "." << version.uMinor << "." << version.uRevision << std::endl;
    return EXIT_SUCCESS;
}
