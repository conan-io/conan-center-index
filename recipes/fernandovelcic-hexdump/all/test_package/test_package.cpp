#include "hexdump.hpp"
#include <stdint.h>
#include <iostream>

template <typename T, T RowSize, T bufSize, bool showFlag>
void testCustomHexdumpBase()
{
    unsigned char data[bufSize];
    for (int i = 0; i < bufSize; ++i)
    {
      data[i] = i;
    }
    std::cout << CustomHexdumpBase<T, RowSize, showFlag>(data, bufSize) << std::endl;
}

int main(int argc, char **argv)
{
  unsigned char data[150];
  for (int i = 0; i < 150; ++i)
  {
    data[i] = i;
  }

  std::cout << Hexdump(data, sizeof(data)) << std::endl;
  std::cout << CustomHexdump<8, true>(data, sizeof(data)) << std::endl;
  std::cout << CustomHexdump<32, false>(data, sizeof(data)) << std::endl;

  testCustomHexdumpBase<uint8_t, 8, 16, true>();
  testCustomHexdumpBase<int8_t, 8, 16, true>();
  testCustomHexdumpBase<uint16_t, 16, 32, true>();
  testCustomHexdumpBase<int16_t, 16, 32, true>();

  return 0;
}
