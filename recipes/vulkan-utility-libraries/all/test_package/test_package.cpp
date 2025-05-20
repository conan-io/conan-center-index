#include <vulkan/utility/vk_safe_struct.hpp>
#include <vulkan/layer/vk_layer_settings.h>

int main(int argc, char ** argv)
{
    const vku::safe_VkDescriptorPoolCreateInfo safe_create_info;

    VkuLayerSettingLogCallback pCallback{nullptr};

    return 0;
}
