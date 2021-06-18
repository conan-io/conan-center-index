#include <cstdlib>
#include <iostream>

#include <windows.h>
#include <streams.h>

int main()
{
    BITMAPINFOHEADER bh;
    memset(&bh, 0, sizeof(BITMAPINFOHEADER));
    bh.biSize = sizeof(BITMAPINFOHEADER);
    bh.biWidth = 1920;
    bh.biHeight = 1080;
    bh.biPlanes = 1;
    bh.biBitCount = 32;
    bh.biCompression = BI_RGB;
    GetBitmapSize(&bh);
    std::cout << "Microsoft DirectShow Base Classes" << std::endl;
    return EXIT_SUCCESS;
}
