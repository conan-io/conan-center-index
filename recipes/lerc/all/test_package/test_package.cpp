#include <Lerc_c_api.h>

#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <iostream>
#include <vector>

typedef unsigned char Byte;    // convenience
typedef unsigned int uint32;

enum lerc_DataType { dt_char = 0, dt_uchar, dt_short, dt_ushort, dt_int, dt_uint, dt_float, dt_double };

void BlobInfo_Print(const uint32* infoArr)
{
  const uint32* ia = infoArr;
  printf("version = %d, dataType = %d, nDim = %d, nCols = %d, nRows = %d, nBands = %d, nValidPixels = %d, blobSize = %d\n",
    ia[0], ia[1], ia[2], ia[3], ia[4], ia[5], ia[6], ia[7]);
}

bool BlobInfo_Equal(const uint32* infoArr, uint32 nDim, uint32 nCols, uint32 nRows, uint32 nBands, uint32 dataType)
{
  const uint32* ia = infoArr;
  return ia[1] == dataType && ia[2] == nDim && ia[3] == nCols && ia[4] == nRows && ia[5] == nBands;
}

// Sample 1: float image, 1 band, with some pixels set to invalid / void, maxZError = 0.1
void sample1() {
  const int h = 512;
  const int w = 512;

  std::vector<float> zImg(w * h);
  std::vector<Byte> maskByteImg(w * h);
  for (int k = 0, i = 0; i < h; ++i) {
    for (int j = 0; j < w; ++j, ++k) {
      zImg[k] = std::sqrt(static_cast<float>(i * i + j * j));    // smooth surface
      zImg[k] += std::rand() % 20;    // add some small amplitude noise

      if (j % 100 == 0 || i % 100 == 0)    // set some void points
        maskByteImg[k] = 0;
      else
        maskByteImg[k] = 1;
    }
  }


  // compress into byte arr

  double maxZErrorWanted = 0.1;
  double eps = 0.0001;    // safety margin (optional), to account for finite floating point accuracy
  double maxZError = maxZErrorWanted - eps;

  uint32 numBytesNeeded = 0;
  uint32 numBytesWritten = 0;

  lerc_status hr = lerc_computeCompressedSize(reinterpret_cast<const void*>(&zImg[0]),    // raw image data, row by row, band by band
    static_cast<uint32>(dt_float), 1, w, h, 1,
#ifdef LERC_VER3_LATER
    1,
#endif
    maskByteImg.data(),         // can give nullptr if all pixels are valid
    maxZError,           // max coding error per pixel, or precision
    &numBytesNeeded);    // size of outgoing Lerc blob

  if (hr)
    std::cout << "lerc_computeCompressedSize(...) failed" << std::endl;

  uint32 numBytesBlob = numBytesNeeded;
  std::vector<Byte> pLercBlob(numBytesBlob);

  hr = lerc_encode(reinterpret_cast<const void*>(&zImg[0]),    // raw image data, row by row, band by band
    static_cast<uint32>(dt_float), 1, w, h, 1,
#ifdef LERC_VER3_LATER
    1,
#endif
    maskByteImg.data(),         // can give nullptr if all pixels are valid
    maxZError,           // max coding error per pixel, or precision
    &pLercBlob[0],           // buffer to write to, function will fail if buffer too small
    numBytesBlob,        // buffer size
    &numBytesWritten);   // num bytes written to buffer

  if (hr)
    std::cout << "lerc_encode(...) failed" << std::endl;

  double ratio = w * h * (0.125 + sizeof(float)) / numBytesBlob;
  std::cout << "sample 1 compression ratio = " << ratio << std::endl;


  // decompress

  uint32 infoArr[10];
  double dataRangeArr[3];
  hr = lerc_getBlobInfo(&pLercBlob[0], numBytesBlob, infoArr, dataRangeArr, 10, 3);
  if (hr)
    std::cout << "lerc_getBlobInfo(...) failed" << std::endl;

  BlobInfo_Print(infoArr);

  if (!BlobInfo_Equal(infoArr, 1, w, h, 1, static_cast<uint32>(dt_float)))
    std::cout << "got wrong lerc info" << std::endl;

  // new empty data storage
  std::vector<float> zImg3(w * h);

  std::vector<Byte> maskByteImg3(w * h);

#ifdef LERC_VER3_LATER
  hr = lerc_decode(&pLercBlob[0], numBytesBlob, 1, maskByteImg3.data(), 1, w, h, 1, static_cast<uint32>(dt_float), reinterpret_cast<void*>(&zImg3[0]));
#else
  hr = lerc_decode(&pLercBlob[0], numBytesBlob, &maskByteImg3[0], 1, w, h, 1, static_cast<uint32>(dt_float), reinterpret_cast<void*>(&zImg3[0]));
#endif
  if (hr)
    std::cout << "lerc_decode(...) failed" << std::endl;

  // compare to orig

  double maxDelta = 0;
  for (int k = 0, i = 0; i < h; i++)
  {
    for (int j = 0; j < w; j++, k++)
    {
      if (maskByteImg3[k] != maskByteImg[k])
        std::cout << "Error in main: decoded valid bytes differ from encoded valid bytes" << std::endl;

      if (maskByteImg3[k])
      {
        double delta = std::fabs(zImg3[k] - zImg[k]);
        if (delta > maxDelta)
          maxDelta = delta;
      }
    }
  }

  std::cout << "max z error per pixel = " << maxDelta << std::endl;
}

int main() {
  sample1();
  return 0;
}
