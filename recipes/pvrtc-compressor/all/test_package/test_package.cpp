#include <iostream>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "RgbBitmap.h"
#include "RgbaBitmap.h"
#include "PvrTcEncoder.h"
#include "PvrTcDecoder.h"

using namespace Javelin;

Bitmap *readTga(const char *filename)
{
    FILE *fp = fopen(filename, "rb");

    fseek(fp, 0, SEEK_END);
    int fsize = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    unsigned char header[18];
    fread(header, 18, 1, fp);

    int bpp = header[16];
    int w = header[12] | (header[13] << 8);
    int h = header[14] | (header[15] << 8);

    Bitmap *bitmap = NULL;
    if (bpp == 24) {
        RgbBitmap *rgb = new RgbBitmap(w, h);
        fread((void *) rgb->data, w * h * 3, 1, fp);
        bitmap = rgb;
    } else if (bpp == 32) {
        RgbaBitmap *rgba = new RgbaBitmap(w, h);
        fread((void *) rgba->data, w * h * 4, 1, fp);
        bitmap = rgba;
    }

    fclose(fp);

    return bitmap;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        std::cerr << "Need at least one argument" << std::endl;
        return 1;
    }

    Bitmap *bitmap = readTga(argv[1]);
    bool isRgb = dynamic_cast<RgbBitmap *>(bitmap) != NULL;

    const int size = bitmap->GetArea() / 2;

    unsigned char *pvrtc = new unsigned char[size];
    memset(pvrtc, 0, size);

    if (isRgb) {
        RgbBitmap *rgb = static_cast<RgbBitmap *>(bitmap);
        ColorRgb<unsigned char> *data = rgb->GetData();
        PvrTcEncoder::EncodeRgb4Bpp(pvrtc, *rgb);
        PvrTcDecoder::DecodeRgb4Bpp(data, bitmap->GetSize(), pvrtc);
    } else {
        RgbaBitmap *rgb = static_cast<RgbaBitmap *>(bitmap);
        ColorRgba<unsigned char> *data = rgb->GetData();
        PvrTcEncoder::EncodeRgba4Bpp(pvrtc, *rgb);
        PvrTcDecoder::DecodeRgba4Bpp(data, bitmap->GetSize(), pvrtc);
    }

    delete bitmap;

    return 0;
}
