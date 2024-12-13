#include <tiffio.hxx>
#include <fstream>

int main()
{
    std::ifstream ifs;
    ifs.open("foo.tif");
    TIFF* tif = TIFFStreamOpen("foo.tif", &ifs);
    TIFFClose(tif);
    return 0;
}
