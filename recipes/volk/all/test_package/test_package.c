#include "volk.h"

#include <stdio.h>

int main() {
    /* Try to initialize volk. This might not work on CI builds,
     * but should have compiled at least. */
    VkResult r = volkInitialize();
    uint32_t version = volkGetInstanceVersion();
    printf("Vulkan version %d.%d.%d initialized.\n",
            VK_VERSION_MAJOR(version),
            VK_VERSION_MINOR(version),
            VK_VERSION_PATCH(version)
            );
}
