#include <webgpu/webgpu.h>
#include <webgpu/wgpu.h>

#include <cstdlib>

int main() {
  uint32_t version = wgpuGetVersion();
  return version != 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
