#include <vulkan/layer/vk_layer_settings.hpp>
#include <iostream>


int main(void) {
    const VkBool32 value_data{VK_TRUE};
    const VkLayerSettingEXT setting{"VK_LAYER_LUNARG_test", "my_setting", VK_LAYER_SETTING_TYPE_BOOL32_EXT, 1, &value_data};
    const VkLayerSettingsCreateInfoEXT layer_settings_create_info{VK_STRUCTURE_TYPE_LAYER_SETTINGS_CREATE_INFO_EXT, nullptr, 1, &setting};

    VkuLayerSettingSet layerSettingSet = VK_NULL_HANDLE;
    std::cout << "layerSettingSet: " << layerSettingSet << std::endl;

    return 0;
}
