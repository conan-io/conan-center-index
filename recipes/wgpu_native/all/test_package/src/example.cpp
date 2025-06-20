#include "webgpu.h"
#include "wgpu.h"

#include <cstdlib>

int main() {
  uint32_t version = wgpuGetVersion();
  return version >= 1246209 ? EXIT_SUCCESS : EXIT_FAILURE;
}
