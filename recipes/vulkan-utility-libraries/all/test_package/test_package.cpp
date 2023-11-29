#include <vulkan/layer/vk_layer_settings.hpp>
#include <iostream>

int main() {
    VkuLayerSettingSet layerSettingSet = VK_NULL_HANDLE;
    vkuCreateLayerSettingSet("VK_LAYER_LUNARG_conan", nullptr, nullptr, nullptr, &layerSettingSet);
    std::cout << VK_EXT_LAYER_SETTINGS_EXTENSION_NAME << std::endl;
    return 0;
}
