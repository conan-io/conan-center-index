#include <stdio.h>
#include <MagickCore/MagickCore.h>

int main(int argc, char **argv)
{
    MagickCoreGenesis(*argv, MagickFalse);

    size_t version;
    printf("ImageMagick version   : %s\n", GetMagickVersion(&version));
    printf("ImageMagick delegates : %s\n", GetMagickDelegates());

    MagickCoreTerminus();
    return 0;
}
