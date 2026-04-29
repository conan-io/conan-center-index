#include "BeepingCoreLib_api.h"

#include <cstdio>
#include <cstdlib>

int main() {
  const char* version = BEEPING_GetVersion();
  if (version == nullptr) {
    std::fprintf(stderr, "BEEPING_GetVersion returned null\n");
    return EXIT_FAILURE;
  }
  std::printf("beeping-core version: %s\n", version);

  void* handle = BEEPING_Create();
  if (handle == nullptr) {
    std::fprintf(stderr, "BEEPING_Create returned null\n");
    return EXIT_FAILURE;
  }
  BEEPING_Destroy(handle);

  std::printf("beeping-core test_package OK\n");
  return EXIT_SUCCESS;
}
