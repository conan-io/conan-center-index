#include <cstdlib>

#include "EtcImage.h"
#include "EtcColorFloatRGBA.h"

int main()
{
    Etc::ColorFloatRGBA* pafrgbaPixels = new Etc::ColorFloatRGBA[256 * 256];

    Etc::Image::EncodingStatus encStatus = Etc::Image::EncodingStatus::SUCCESS;

    delete[] pafrgbaPixels;
    pafrgbaPixels = nullptr;

    return EXIT_SUCCESS;
}
