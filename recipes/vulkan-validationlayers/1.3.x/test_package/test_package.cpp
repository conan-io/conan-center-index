#include <vulkan/vk_format_utils.h>

#include <iostream>

int main() {
  std::cout << "VK_FORMAT_D16_UNORM " << (FormatIsDepthOnly(VK_FORMAT_D16_UNORM) ? "is" : "is not") << " depth only" << std::endl;
  return 0;
}
