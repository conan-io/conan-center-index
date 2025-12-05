#include <vulkan/vulkan.h>

#include <iostream>

VkApplicationInfo initAppInfo() {
  VkApplicationInfo appInfo = {};
  appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
  appInfo.pApplicationName = "Hello Vulkan";
  appInfo.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
  appInfo.pEngineName = "No Engine";
  appInfo.engineVersion = VK_MAKE_VERSION(1, 0, 0);
  appInfo.apiVersion = VK_API_VERSION_1_0;
  return appInfo;
}

int main() {
    const VkApplicationInfo app_info = initAppInfo();

    const char* layers[] = {"VK_LAYER_KHRONOS_validation", "VK_LAYER_KHRONOS_profiles"};

    const VkInstanceCreateInfo inst_create_info = {
        VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, nullptr, 0,
        &app_info,
        //static_cast<uint32_t>(std::size(layers)), layers,
        0, nullptr,
        0, nullptr
    };

    VkInstance instance = VK_NULL_HANDLE;
    VkResult result = vkCreateInstance(&inst_create_info, nullptr, &instance);
    std::cout << result << std::endl;
}
