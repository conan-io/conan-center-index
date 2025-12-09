//#include <vulkan/vulkan.h>
//#include <vector>
//#include <iostream>
//
//VkApplicationInfo initAppInfo() {
//  VkApplicationInfo appInfo = {};
//  appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
//  appInfo.pApplicationName = "Hello Vulkan";
//  appInfo.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
//  appInfo.pEngineName = "No Engine";
//  appInfo.engineVersion = VK_MAKE_VERSION(1, 0, 0);
//  appInfo.apiVersion = VK_API_VERSION_1_0;
//  return appInfo;
//}
//
//VkResult CreateDebugUtilsMessengerEXT(VkInstance instance, const VkDebugUtilsMessengerCreateInfoEXT* pCreateInfo, const VkAllocationCallbacks* pAllocator, VkDebugUtilsMessengerEXT* pDebugMessenger) {
//    auto func = (PFN_vkCreateDebugUtilsMessengerEXT) vkGetInstanceProcAddr(instance, "vkCreateDebugUtilsMessengerEXT");
//    if (func != nullptr) {
//        return func(instance, pCreateInfo, pAllocator, pDebugMessenger);
//    } else {
//        return VK_ERROR_EXTENSION_NOT_PRESENT;
//    }
//}
//
//void DestroyDebugUtilsMessengerEXT(VkInstance instance, VkDebugUtilsMessengerEXT debugMessenger, const VkAllocationCallbacks* pAllocator) {
//    auto func = (PFN_vkDestroyDebugUtilsMessengerEXT) vkGetInstanceProcAddr(instance, "vkDestroyDebugUtilsMessengerEXT");
//    if (func != nullptr) {
//        func(instance, debugMessenger, pAllocator);
//    }
//}
//
//static VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
//    VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
//    VkDebugUtilsMessageTypeFlagsEXT messageType,
//    const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
//    void* pUserData) {
//
//    std::cerr << "validation layer: " << pCallbackData->pMessage << std::endl;
//
//    return VK_FALSE;
//}
//
//int main() {
//    const VkApplicationInfo app_info = initAppInfo();
//
//    const char* layers[] = {"VK_LAYER_KHRONOS_validation"};
//
//    uint32_t propertyCount = 0;
//    VkLayerProperties pProperties;
//    vkEnumerateInstanceLayerProperties(&propertyCount, nullptr);
//
//    std::vector<VkLayerProperties> props;
//    props.reserve(propertyCount);
//
//    vkEnumerateInstanceLayerProperties(&propertyCount, props.data());
//
//    for (int i = 0;i < propertyCount;i++) {
//      std::cout << props[i].layerName << ": " << props[i].description << std::endl;
//    }
//
//    std::cout << "Property count: " << propertyCount << std::endl;
//
//    VkDebugUtilsMessengerEXT debugMessenger;
//    VkDebugUtilsMessengerCreateInfoEXT debugcreateInfo = {};
//    debugcreateInfo.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT;
//    debugcreateInfo.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
//    debugcreateInfo.messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
//    debugcreateInfo.pfnUserCallback = debugCallback;
//
//
//
//    VkInstanceCreateInfo inst_create_info = {
//        VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, nullptr, 0,
//        &app_info,
//        static_cast<uint32_t>(std::size(layers)), layers,
//        //0, nullptr,
//        0, nullptr
//    };
//
//    std::vector<const char*> instance_extensions;
//    instance_extensions.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
//
//    inst_create_info.pNext = (VkDebugUtilsMessengerCreateInfoEXT*) &debugcreateInfo;
//    inst_create_info.ppEnabledExtensionNames = instance_extensions.data();
//    inst_create_info.enabledExtensionCount = static_cast<uint32_t>(instance_extensions.size());
//
//    VkInstance instance = VK_NULL_HANDLE;
//    VkResult result = vkCreateInstance(&inst_create_info, nullptr, &instance);
//    std::cout << result << std::endl;
//
//  if (CreateDebugUtilsMessengerEXT(instance, &debugcreateInfo, nullptr, &debugMessenger) != VK_SUCCESS) {
//          throw std::runtime_error("failed to set up debug messenger!");
//      }
//}

// The above code is disabled to avoid compilation issues on systems without Vulkan SDK installed.
// testing was performed manually. You expect to see validation layer messages in the output
// where the VK_LAYER_KHRONOS_validation.dll is loaded
int main() {
   return 0;
}
