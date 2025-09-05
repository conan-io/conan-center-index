#include <vulkan/layer/vk_layer_settings.h>
#include <vulkan/utility/vk_safe_struct.hpp>
#include <vulkan/utility/vk_struct_helper.hpp>


int main() {
    vku::safe_VkInstanceCreateInfo safe_info;
    VkApplicationInfo app = vku::InitStructHelper();
    app.pApplicationName = "test";
    app.applicationVersion = 42;

    VkDebugUtilsMessengerCreateInfoEXT debug_ci = vku::InitStructHelper();
    debug_ci.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;

    VkInstanceCreateInfo info = vku::InitStructHelper();
    info.pApplicationInfo = &app;
    info.pNext = &debug_ci;

    safe_info.initialize(&info);

    VkuLayerSettingSet layerSettingSet = VK_NULL_HANDLE;
    vkuCreateLayerSettingSet("VK_LAYER_LUNARG_test", nullptr, nullptr, nullptr, &layerSettingSet);

    return 0;
}
