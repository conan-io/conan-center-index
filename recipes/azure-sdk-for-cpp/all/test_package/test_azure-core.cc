#include <iostream>
#include <azure/core.hpp>

int main()
{
  std::vector<uint8_t> data = {1, 2, 3, 4};
  Azure::Core::IO::MemoryBodyStream stream(data);

  return 0;
}
