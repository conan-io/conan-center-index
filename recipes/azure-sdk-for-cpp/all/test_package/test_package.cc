#include <iostream>

// Include the necessary SDK headers
#include <azure/core.hpp>
#include <azure/storage/blobs.hpp>

// Add appropriate using namespace directives
using namespace Azure::Storage;
using namespace Azure::Storage::Blobs;

int main()
{
  BlobAudience audience{"TEST"};

  std::vector<uint8_t> data = {1, 2, 3, 4};
  Azure::Core::IO::MemoryBodyStream stream(data);

  return 0;
}
