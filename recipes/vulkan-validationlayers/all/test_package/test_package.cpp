#include <vulkan/vulkan.h>

#include <iostream>

int main() {
	const VkApplicationInfo app_info{
	    .sType            = VK_STRUCTURE_TYPE_APPLICATION_INFO,
	    .pApplicationName = "Conan Test Package",
	    .pEngineName      = "Conan",
	    .apiVersion       = VK_API_VERSION_1_0
	};

    const char* layers[] = {"VK_LAYER_KHRONOS_validation"};

    const VkInstanceCreateInfo inst_create_info = {
        VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, nullptr, 0,
        &app_info,
        static_cast<uint32_t>(std::size(layers)), layers,
        0, nullptr
    };

    VkInstance instance = VK_NULL_HANDLE;
    VkResult result = vkCreateInstance(&inst_create_info, nullptr, &instance);
    if (result != VK_SUCCESS) {
        std::cerr << "Could not instantiate layer\n";
        return 1;
    }

    return 0;
}
