#include <vulkan/vulkan.hpp>

static std::string AppName    = "01_InitInstance";
static std::string EngineName = "Vulkan.hpp";

int main()
{
    vk::ApplicationInfo applicationInfo( "test_package", 1, "vulkan", 1, VK_API_VERSION_1_1 );
    return 0;
}
