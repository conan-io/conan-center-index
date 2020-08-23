#include "volk.h"

#include <stdio.h>

int main() {
    VkResult r = volkInitialize();
    if (r == VK_SUCCESS){
        uint32_t version = volkGetInstanceVersion();
        printf("Vulkan version %d.%d.%d initialized.\n",
            VK_VERSION_MAJOR(version),
            VK_VERSION_MINOR(version),
            VK_VERSION_PATCH(version)
            );
    }
    return 0;
}
