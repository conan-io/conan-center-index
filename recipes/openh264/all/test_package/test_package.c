#include <stdio.h>
#include <wels/codec_api.h>

int main()
{
    OpenH264Version version = WelsGetCodecVersion();
    printf("OpenH264 version: %d.%d.%d\n", version.uMajor, version.uMinor, version.uRevision);
    return 0;
}
