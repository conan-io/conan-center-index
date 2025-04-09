#include "gdcmReader.h"

int main()
{
  gdcm::Reader reader;
  reader.SetFileName("myFileName");
  return 0;
}
