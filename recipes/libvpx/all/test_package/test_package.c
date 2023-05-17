#include <vpx/vpx_codec.h>

#include <stdio.h>

int main()
{
    printf("vpx version %s\n", vpx_codec_version_str());
    return 0;
}
