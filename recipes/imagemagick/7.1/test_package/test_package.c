#include <stdio.h>
#include <MagickCore/MagickCore.h>

int main()
{
    size_t version, range, depth;
    printf("Imagemagick version      : %s\n", GetMagickVersion(&version));
    printf("ImageMagick release data : %s\n", GetMagickReleaseDate());
    printf("ImageMagick quantum range: %s\n", GetMagickQuantumRange(&range));
    printf("ImageMagick quantum depth: %s\n", GetMagickQuantumDepth(&depth));
    printf("ImageMagick package name : %s\n", GetMagickPackageName());
    printf("ImageMagick license      : %s\n", GetMagickLicense());
    printf("ImageMagick home URL     : %s\n", GetMagickHomeURL());
    printf("ImageMagick features     : %s\n", GetMagickFeatures());
    printf("ImageMagick delegates    : %s\n", GetMagickDelegates());
    printf("ImageMagick copyright    : %s\n", GetMagickCopyright());

    FILE *fp;
    fp = fopen("delegates.txt", "w+");
    fputs(GetMagickDelegates(), fp);
    fclose(fp);

    return 0;
}
