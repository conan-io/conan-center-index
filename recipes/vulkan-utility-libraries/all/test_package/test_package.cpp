#include <vulkan/vulkan.h>
#include <vulkan/vk_enum_string_helper.h>
#include <vulkan/vk_format_utils.h>
#include <vulkan/vk_struct_string_helper.h>
#include <iostream>
#include <cassert>

int main() {
    // Test vk_enum_string_helper.h
    const char* result_str = string_VkResult(VK_SUCCESS);
    std::cout << "VK_SUCCESS string: " << result_str << std::endl;
    assert(result_str != nullptr);

    // Test vk_format_utils.h
    VkFormat format = VK_FORMAT_R8G8B8A8_UNORM;
    bool is_depth = vkuFormatIsDepth(format);
    bool is_stencil = vkuFormatIsStencil(format);
    std::cout << "Format " << format << " is depth: " << is_depth << ", is stencil: " << is_stencil << std::endl;
    assert(!is_depth && !is_stencil);

    // Test vk_struct_string_helper.h
    VkExtent2D extent = {1920, 1080};
    std::string extent_str = string_VkExtent2D(&extent);
    std::cout << "Extent string: " << extent_str << std::endl;
    assert(!extent_str.empty());

    std::cout << "All tests passed!" << std::endl;
    return 0;
}