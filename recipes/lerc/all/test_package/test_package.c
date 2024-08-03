#include <Lerc_c_api.h>

#include <stdint.h>

int main() {
  const uint32_t numBytesBlob = 275714;
  uint8_t pLercBlob[1000000];
  uint32_t infoArr[10];
  double dataRangeArr[3];
  lerc_getBlobInfo(&pLercBlob[0], numBytesBlob, infoArr, dataRangeArr, 10, 3);
}
