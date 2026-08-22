#include <tiffio.h>

int main()
{
    TIFF* tif = TIFFOpen("foo.tif", "w");
    TIFFClose(tif);
    return 0;
}
