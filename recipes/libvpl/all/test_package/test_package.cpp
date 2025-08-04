#include <vpl/mfx.h>
#include <iostream>
#include <cstdlib>

int main() {
    // Print the VPL API version
    mfxVersion version = { {0, 1} };
    mfxStatus status = MFXQueryVersion(nullptr, &version);

    if (status == MFX_ERR_NONE) {
        std::cout << "VPL API version: " << version.Major << "." << version.Minor << std::endl;
    } else {
        std::cout << "Failed to query VPL API version. Status: " << status << std::endl;
    }

    // Initialize VPL session
    mfxLoader loader = MFXLoad();
    if (!loader) {
        std::cout << "Failed to create VPL loader" << std::endl;
        return EXIT_FAILURE;
    }

    // Clean up
    MFXUnload(loader);

    return EXIT_SUCCESS;
}
