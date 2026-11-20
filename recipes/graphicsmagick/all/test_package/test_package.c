#include <stdio.h>
#include <magick/api.h>

int main(int argc, char **argv)
{
    unsigned long version;
    (void)argc;

    InitializeMagick(argv[0]);
    printf("GraphicsMagick version  : %s\n", GetMagickVersion(&version));
    printf("GraphicsMagick copyright: %s\n", GetMagickCopyright());
    DestroyMagick();

    return 0;
}
