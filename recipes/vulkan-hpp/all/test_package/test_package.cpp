#define VULKAN_HPP_NO_CONSTRUCTORS
#include <vulkan.hpp>

int main()
{
    // initialize the vk::ApplicationInfo structure
    vk::ApplicationInfo applicationInfo{ .pApplicationName   = "ConanTestApp",
                                         .applicationVersion = 1,
                                         .pEngineName        = "ConanTestEngine",
                                         .engineVersion      = 1,
                                         .apiVersion         = VK_API_VERSION_1_1 };
        
    vk::InstanceCreateInfo instanceCreateInfo{ .pApplicationInfo = & applicationInfo };

    return EXIT_SUCCESS;
}
