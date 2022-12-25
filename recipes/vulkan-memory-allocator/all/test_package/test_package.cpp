#define VMA_STATIC_VULKAN_FUNCTIONS 0
#define VMA_IMPLEMENTATION
#include <vk_mem_alloc.h>

int main()
{
  // Load function pointers...
  // vmaVmaVulkanFunctions vulkanFunctions{};
  // vulkavulkanFunctions.vkAllocateMemory = ... ;
  // ...

  VmaAllocatorCreateInfo allocatorInfo{}; (void)allocatorInfo;
  // allocatorInfo.instance         = instance;
  // allocatorInfo.physicalDevice   = physicalDevice;
  // allocatorInfo.device           = device;
  // allocatorInfo.pVulkanFunctions = &vulkanFunctions;

  VmaAllocator allocator; (void)allocator;
  // vmaCreateAllocator(&allocatorInfo, &allocator);
}
