#include <vulkan/vulkan.hpp>

int main()
{
    vk::ApplicationInfo applicationInfo( "test_package", 1, "vulkan", 1, VK_API_VERSION_1_1 );
    return 0;
}
