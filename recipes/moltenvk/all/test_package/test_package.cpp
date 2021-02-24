#include <iostream>

#include <vulkan/vulkan.hpp>

int main()
{
    vk::ApplicationInfo appInfo;
    appInfo.pApplicationName = "ConanTestApp";
    appInfo.pEngineName = "ConanTestEngine";
    appInfo.apiVersion = VK_API_VERSION_1_0;

    vk::InstanceCreateInfo instanceCreateInfo;
    instanceCreateInfo.pApplicationInfo = &appInfo;

    try
    {
        vk::Instance instance = vk::createInstance(instanceCreateInfo);

        auto physicalDevices = instance.enumeratePhysicalDevices();
        auto physicalDevice = physicalDevices[0];
        auto deviceProperties = physicalDevice.getProperties();
        auto deviceMemoryProperties = physicalDevice.getMemoryProperties();

        std::cout << "Vulkan device created" << std::endl;
        std::cout << "API Version:    " << deviceProperties.apiVersion << std::endl;
        std::cout << "Driver Version: " << deviceProperties.driverVersion << std::endl;
        std::cout << "Device Name:    " << deviceProperties.deviceName << std::endl;
        std::cout << "Device Type:    " << vk::to_string(deviceProperties.deviceType) << std::endl;
        std::cout << "Memory Heaps:   " << deviceMemoryProperties.memoryHeapCount << std::endl;
    }
    catch(const vk::SystemError& e)
    {
        std::cerr << e.what() << '\n';
    }

    return 0;
}
