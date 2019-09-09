#include <stdio.h>
#include <webp/decode.h>

int main(void)
{
    int version = WebPGetDecoderVersion();
    printf("Webp Decoder version: %d\n", version);

    return 0;
}