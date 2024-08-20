#include <Lerc_c_api.h>

#include <cstdint>
#include <vector>

int main() {
  uint32_t numBytesBlob = 275714;
  std::vector<uint8_t> pLercBlob(numBytesBlob);
  uint32_t infoArr[10];
  double dataRangeArr[3];
  lerc_getBlobInfo(&pLercBlob[0], numBytesBlob, infoArr, dataRangeArr, 10, 3);
}
